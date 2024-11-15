from pydantic import BaseModel
from typing import List, Optional, Any, Dict


class FrameObject(BaseModel):
    id: str  # object id str uuid
    objectColor: str  # hex color

    class Config:
        from_attributes = True


class FrameCover(BaseModel):
    frame_number: int
    image_base64: str
    objects: List[FrameObject] = []

    class Config:
        from_attributes = True
