from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base

class BlogPost(Base):
    """Blog post model with industry and location relationships."""
    
    # Content fields
    industry_id = Column(Integer, ForeignKey("industry.id"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False, index=True)
    topic = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    style = Column(String(50), nullable=False, default="professional")
    
    # Metadata
    tokens_used = Column(Integer)
    metadata = Column(JSON)
    
    # Relationships
    industry = relationship("Industry", back_populates="posts")
    location = relationship("Location", back_populates="posts")
    
    def __repr__(self):
        return f"<BlogPost(id={self.id}, topic='{self.topic[:30]}...', industry_id={self.industry_id})>" 