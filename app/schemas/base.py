from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM model conversion
        json_encoders={
            datetime: lambda v: v.isoformat()  # ISO format for dates
        }
    )

class TimestampSchema(BaseSchema):
    """Schema mixin for timestamp fields."""
    created_at: datetime
    updated_at: datetime

class IDSchema(BaseSchema):
    """Schema mixin for ID field."""
    id: int

class BaseAPIResponse(BaseSchema):
    """Base response schema with status and message."""
    success: bool = True
    message: Optional[str] = None 