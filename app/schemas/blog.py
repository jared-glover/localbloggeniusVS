from typing import List, Optional
from pydantic import Field, validator
from datetime import datetime
from .base import BaseSchema, TimestampSchema, IDSchema, BaseAPIResponse

class BlogPostCreate(BaseSchema):
    """Schema for creating a new blog post."""
    industry: str = Field(..., min_length=2, max_length=100)
    location: str = Field(..., min_length=2, max_length=100)
    topic: str = Field(..., min_length=5, max_length=200)
    style: Optional[str] = Field("professional", min_length=3, max_length=50)
    
    @validator('industry', 'location', 'topic')
    def validate_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v

class BlogPostResponse(IDSchema, TimestampSchema):
    """Schema for blog post response."""
    industry: str
    location: str
    topic: str
    content: str
    style: str
    tokens_used: Optional[int] = None
    metadata: Optional[dict] = None

class BlogPostList(BaseAPIResponse):
    """Schema for listing blog posts."""
    total: int
    items: List[BlogPostResponse]
    
class BlogPostGenerated(BaseAPIResponse):
    """Schema for generated blog post response."""
    data: BlogPostResponse

class BlogPostStats(BaseSchema):
    """Schema for blog post statistics."""
    total_posts: int
    posts_by_industry: dict
    posts_by_location: dict
    average_tokens: Optional[float]
    last_generated: Optional[datetime] 