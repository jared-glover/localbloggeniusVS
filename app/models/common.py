from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.orm import relationship
from .base import Base

class Industry(Base):
    """Industry model with relationship to blog posts."""
    
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    category = Column(String(100))
    
    # Relationships
    posts = relationship("BlogPost", back_populates="industry", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Industry(id={self.id}, name='{self.name}')>"

class Location(Base):
    """Location model with relationship to blog posts."""
    
    name = Column(String(100), nullable=False, index=True)
    state = Column(String(100))
    country = Column(String(100), nullable=False)
    timezone = Column(String(50))
    metadata = Column(JSON)
    
    # Relationships
    posts = relationship("BlogPost", back_populates="location", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}', country='{self.country}')>"
    
    @property
    def full_name(self) -> str:
        """Get the full location name including state and country."""
        parts = [self.name]
        if self.state:
            parts.append(self.state)
        parts.append(self.country)
        return ", ".join(parts) 