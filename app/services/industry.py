from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
import logging
from app.models import Industry, BlogPost
from app.schemas.common import IndustryCreate, IndustryResponse
from .base import BaseService

logger = logging.getLogger(__name__)

class IndustryService(BaseService[Industry, IndustryCreate, IndustryResponse]):
    """Service for managing industries with categorization."""
    
    def __init__(self):
        super().__init__(Industry)
        self.categories = {
            "technology": [
                "software", "it", "cybersecurity", "web development",
                "mobile apps", "cloud computing", "artificial intelligence"
            ],
            "healthcare": [
                "medical", "dental", "pharmacy", "wellness", "fitness",
                "mental health", "healthcare technology"
            ],
            "retail": [
                "fashion", "electronics", "groceries", "furniture",
                "e-commerce", "luxury goods", "sporting goods"
            ],
            "services": [
                "consulting", "legal", "accounting", "marketing",
                "design", "cleaning", "maintenance"
            ],
            "hospitality": [
                "restaurants", "hotels", "tourism", "events",
                "catering", "travel", "entertainment"
            ]
        }
    
    async def create_with_category(
        self,
        db: Session,
        *,
        name: str,
        description: Optional[str] = None
    ) -> Industry:
        """Create a new industry with automatic categorization."""
        try:
            # Determine category
            category = self._categorize_industry(name)
            
            industry = Industry(
                name=name,
                description=description,
                category=category
            )
            
            db.add(industry)
            db.commit()
            db.refresh(industry)
            return industry
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating industry: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_industry_stats(self, db: Session) -> Dict[str, Any]:
        """Get statistics about industries."""
        try:
            total = await self.count(db)
            
            # Get categories with counts
            categories = (
                db.query(
                    Industry.category,
                    func.count(Industry.id).label("industry_count"),
                    func.count(Industry.posts).label("post_count")
                )
                .group_by(Industry.category)
                .all()
            )
            
            # Get top industries by post count
            top_industries = (
                db.query(
                    Industry.name,
                    Industry.category,
                    func.count(Industry.posts).label("post_count")
                )
                .group_by(Industry.name, Industry.category)
                .order_by(func.count(Industry.posts).desc())
                .limit(5)
                .all()
            )
            
            # Get average post length by industry
            avg_lengths = (
                db.query(
                    Industry.name,
                    func.avg(func.length(BlogPost.content)).label("avg_length")
                )
                .join(BlogPost)
                .group_by(Industry.name)
                .all()
            )
            
            return {
                "total_industries": total,
                "categories": {
                    category: {
                        "industry_count": ind_count,
                        "post_count": post_count
                    }
                    for category, ind_count, post_count in categories
                },
                "top_industries": [
                    {
                        "name": name,
                        "category": category,
                        "post_count": count
                    }
                    for name, category, count in top_industries
                ],
                "average_lengths": {
                    name: round(float(avg), 2)
                    for name, avg in avg_lengths
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting industry stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving industry statistics"
            )
    
    def _categorize_industry(self, name: str) -> str:
        """Categorize an industry based on its name."""
        name_lower = name.lower()
        
        # Check each category's keywords
        for category, keywords in self.categories.items():
            if any(keyword in name_lower for keyword in keywords):
                return category
        
        return "other"  # Default category
    
    async def get_related_industries(
        self,
        db: Session,
        industry_name: str,
        limit: int = 5
    ) -> List[Industry]:
        """Get related industries based on category and post patterns."""
        try:
            industry = (
                db.query(Industry)
                .filter(Industry.name == industry_name)
                .first()
            )
            
            if not industry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Industry not found"
                )
            
            # Get industries in the same category
            related = (
                db.query(Industry)
                .filter(
                    Industry.category == industry.category,
                    Industry.name != industry_name
                )
                .limit(limit)
                .all()
            )
            
            return related
            
        except Exception as e:
            logger.error(f"Error getting related industries: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error finding related industries"
            )

# Global industry service instance
industry_service = IndustryService() 