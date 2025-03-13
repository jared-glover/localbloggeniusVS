from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models import BlogPost, Industry, Location
from app.schemas.blog import BlogPostCreate, BlogPostResponse
from app.core.ai import ai_service
from .base import BaseService
import logging

logger = logging.getLogger(__name__)

class BlogService(BaseService[BlogPost, BlogPostCreate, BlogPostResponse]):
    """Service for managing blog posts with AI generation."""
    
    def __init__(self):
        super().__init__(BlogPost)
    
    async def create_blog_post(
        self,
        db: Session,
        *,
        industry_name: str,
        location_name: str,
        topic: str,
        style: Optional[str] = "professional"
    ) -> BlogPost:
        """Create a new blog post with AI-generated content."""
        try:
            # Get or create industry
            industry = await self._get_or_create_industry(db, industry_name)
            
            # Get or create location
            location = await self._get_or_create_location(db, location_name)
            
            # Generate content using AI
            generated = await ai_service.generate_blog_content(
                industry=industry_name,
                location=location_name,
                topic=topic,
                style=style
            )
            
            # Create blog post
            blog_post = BlogPost(
                industry_id=industry.id,
                location_id=location.id,
                topic=topic,
                content=generated["content"],
                style=style,
                tokens_used=generated["tokens_used"],
                metadata={
                    "finish_reason": generated["finish_reason"],
                    "generation_date": func.now()
                }
            )
            
            db.add(blog_post)
            db.commit()
            db.refresh(blog_post)
            return blog_post
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating blog post: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_blog_stats(self, db: Session) -> Dict[str, Any]:
        """Get statistics about blog posts."""
        try:
            total_posts = await self.count(db)
            
            # Get posts by industry
            industry_stats = (
                db.query(
                    Industry.name,
                    func.count(BlogPost.id).label("post_count")
                )
                .join(BlogPost)
                .group_by(Industry.name)
                .all()
            )
            
            # Get posts by location
            location_stats = (
                db.query(
                    Location.name,
                    func.count(BlogPost.id).label("post_count")
                )
                .join(BlogPost)
                .group_by(Location.name)
                .all()
            )
            
            # Calculate average tokens
            avg_tokens = (
                db.query(func.avg(BlogPost.tokens_used))
                .scalar() or 0
            )
            
            # Get last generated post date
            last_generated = (
                db.query(BlogPost.created_at)
                .order_by(BlogPost.created_at.desc())
                .first()
            )
            
            return {
                "total_posts": total_posts,
                "posts_by_industry": {
                    name: count for name, count in industry_stats
                },
                "posts_by_location": {
                    name: count for name, count in location_stats
                },
                "average_tokens": round(float(avg_tokens), 2),
                "last_generated": last_generated[0] if last_generated else None
            }
            
        except Exception as e:
            logger.error(f"Error getting blog stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving blog statistics"
            )
    
    async def get_posts_by_industry(
        self,
        db: Session,
        industry_name: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[BlogPost]:
        """Get all posts for a specific industry."""
        return (
            db.query(BlogPost)
            .join(Industry)
            .filter(Industry.name == industry_name)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    async def get_posts_by_location(
        self,
        db: Session,
        location_name: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[BlogPost]:
        """Get all posts for a specific location."""
        return (
            db.query(BlogPost)
            .join(Location)
            .filter(Location.name == location_name)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    async def _get_or_create_industry(
        self,
        db: Session,
        name: str
    ) -> Industry:
        """Get existing industry or create new one."""
        industry = (
            db.query(Industry)
            .filter(Industry.name == name)
            .first()
        )
        
        if not industry:
            industry = Industry(name=name)
            db.add(industry)
            db.commit()
            db.refresh(industry)
        
        return industry
    
    async def _get_or_create_location(
        self,
        db: Session,
        name: str
    ) -> Location:
        """Get existing location or create new one."""
        location = (
            db.query(Location)
            .filter(Location.name == name)
            .first()
        )
        
        if not location:
            # For simplicity, we're just storing the name
            # In a real app, you might want to validate and get country/state
            location = Location(
                name=name,
                country="Unknown"  # Default value
            )
            db.add(location)
            db.commit()
            db.refresh(location)
        
        return location

# Global blog service instance
blog_service = BlogService() 