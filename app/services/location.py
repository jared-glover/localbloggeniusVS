from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
import aiohttp
import logging
from app.models import Location
from app.schemas.common import LocationCreate, LocationResponse, LocationSuggestion
from .base import BaseService

logger = logging.getLogger(__name__)

class LocationService(BaseService[Location, LocationCreate, LocationResponse]):
    """Service for managing locations with geocoding capabilities."""
    
    def __init__(self):
        super().__init__(Location)
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            "User-Agent": "LocalBlogGenius/1.0"  # Required by Nominatim
        }
    
    async def search_locations(
        self,
        query: str,
        limit: int = 5
    ) -> List[LocationSuggestion]:
        """Search locations using OpenStreetMap Nominatim API."""
        try:
            params = {
                "q": query,
                "format": "json",
                "limit": limit,
                "addressdetails": 1
            }
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(self.nominatim_url, params=params) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Geocoding service unavailable"
                        )
                    
                    results = await response.json()
                    
                    return [
                        LocationSuggestion(
                            name=self._get_place_name(result),
                            full_name=self._format_full_name(result),
                            type=result.get("type", "unknown"),
                            metadata={
                                "lat": result.get("lat"),
                                "lon": result.get("lon"),
                                "osm_type": result.get("osm_type"),
                                "class": result.get("class")
                            }
                        )
                        for result in results
                    ]
        
        except aiohttp.ClientError as e:
            logger.error(f"Error searching locations: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Error connecting to geocoding service"
            )
        except Exception as e:
            logger.error(f"Unexpected error in location search: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing location search"
            )
    
    async def get_location_stats(self, db: Session) -> Dict[str, Any]:
        """Get statistics about locations."""
        try:
            total = await self.count(db)
            
            # Get countries with post counts
            countries = (
                db.query(
                    Location.country,
                    func.count(Location.id).label("location_count"),
                    func.count(Location.posts).label("post_count")
                )
                .group_by(Location.country)
                .all()
            )
            
            # Get top locations by post count
            top_locations = (
                db.query(
                    Location.name,
                    Location.country,
                    func.count(Location.posts).label("post_count")
                )
                .group_by(Location.name, Location.country)
                .order_by(func.count(Location.posts).desc())
                .limit(5)
                .all()
            )
            
            return {
                "total_locations": total,
                "countries": {
                    country: {
                        "location_count": loc_count,
                        "post_count": post_count
                    }
                    for country, loc_count, post_count in countries
                },
                "top_locations": [
                    {
                        "name": name,
                        "country": country,
                        "post_count": count
                    }
                    for name, country, count in top_locations
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting location stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving location statistics"
            )
    
    def _get_place_name(self, result: Dict[str, Any]) -> str:
        """Extract the main place name from Nominatim result."""
        address = result.get("address", {})
        
        # Try different address components in order of preference
        for key in ["city", "town", "village", "suburb", "municipality"]:
            if address.get(key):
                return address[key]
        
        # Fallback to display name
        return result.get("display_name", "").split(",")[0]
    
    def _format_full_name(self, result: Dict[str, Any]) -> str:
        """Format the full location name from Nominatim result."""
        address = result.get("address", {})
        parts = []
        
        # Add main place name
        place_name = self._get_place_name(result)
        if place_name:
            parts.append(place_name)
        
        # Add state/province if available
        state = address.get("state") or address.get("province")
        if state and state not in parts:
            parts.append(state)
        
        # Add country
        country = address.get("country")
        if country and country not in parts:
            parts.append(country)
        
        return ", ".join(parts)

# Global location service instance
location_service = LocationService() 