from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReportBase(BaseModel):
    text: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    text: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    is_critical: Optional[bool] = None

class ReportResponse(ReportBase):
    id: int
    user_id: int
    is_critical: bool
    status: str
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ReportListResponse(BaseModel):
    id: int
    user_id: int
    text: str
    is_critical: bool
    status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class EmergencyReportCreate(BaseModel):
    text: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
