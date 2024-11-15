from pydantic import BaseModel, Field
from .video import VideoOutDetailed


class AiModel(BaseModel):
    ai_model_id: int
    ai_model_name: str
    checkpoint_path: str
    config_path: str

    class Config:
        from_attributes = True


class InitModelRequest(BaseModel):
    ai_model_id: int = Field(alias="model_id")
    video_id: int
    class Config:
        from_attributes = True
