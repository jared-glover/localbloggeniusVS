from typing import List, Optional
from pydantic import Field
from .base import BaseSchema, BaseAPIResponse, IDSchema, TimestampSchema

class IndustryCreate(BaseSchema):
    """Schema for creating a new industry."""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)

class IndustryResponse(IDSchema, TimestampSchema):
    """Schema for industry response."""
    name: str
    description: Optional[str]
    category: Optional[str]
    post_count: Optional[int] = 0

class IndustryList(BaseAPIResponse):
    """Schema for listing industries."""
    total: int
    items: List[IndustryResponse]

class LocationCreate(BaseSchema):
    """Schema for creating a new location."""
    name: str = Field(..., min_length=2, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: str = Field(..., max_length=100)
    timezone: Optional[str] = None
    metadata: Optional[dict] = None

class LocationResponse(IDSchema, TimestampSchema):
    """Schema for location response."""
    name: str
    state: Optional[str]
    country: str
    timezone: Optional[str]
    metadata: Optional[dict]
    post_count: Optional[int] = 0

class LocationList(BaseAPIResponse):
    """Schema for listing locations."""
    total: int
    items: List[LocationResponse]

class LocationSuggestion(BaseSchema):
    """Schema for location autocomplete suggestions."""
    name: str
    full_name: str  # Includes state/country
    type: str  # city, state, country, etc.
    metadata: Optional[dict] = None

class LocationSuggestionList(BaseAPIResponse):
    """Schema for list of location suggestions."""
    items: List[LocationSuggestion] 