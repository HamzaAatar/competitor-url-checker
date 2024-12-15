from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class JobCreate(BaseModel):
    input_data: Dict


class JobResponse(BaseModel):
    id: int
    status: str
    input_data: Dict
    result: Optional[Dict]
    created_at: datetime
    updated_at: datetime
