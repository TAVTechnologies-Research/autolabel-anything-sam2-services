from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from enums import VideoStatusEnum


class VideoIn(BaseModel):
    video_name: str
    video_path: str

    class Config:
        from_attributes = True


class VideoOut(BaseModel):
    video_id: int
    video_name: str
    status: str
    created_at: datetime
    file_size: int  # in bytes

    class Config:
        from_attributes = True


class VideoOutDetailed(VideoOut):
    video_height: int
    video_width: int
    video_duration: int
    video_path: str
    frames_path: str
    frame_count: Optional[int] = None

    class Config:
        from_attributes = True


class VideoInformation(BaseModel):
    video_width: int
    video_height: int
    video_duration: int
    video_fps: float

    class Config:
        from_attributes = True


class VideoStatus(BaseModel):
    status: VideoStatusEnum

    class Config:
        from_attributes = True
