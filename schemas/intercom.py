from pydantic import BaseModel, field_validator, model_validator

from typing import Literal, Union, Any
from typing_extensions import Self

from .ai_model import AiModel
from .video import VideoOutDetailed


class InitModelIntercom(BaseModel):
    ai_model: AiModel
    video: VideoOutDetailed

    class Config:
        from_attributes = True


class Intercom(BaseModel):
    task_type: Literal["initialize_model", "terminate_model", "reset"]
    # task: Union[InitModelIntercom, None]
    task: Union[InitModelIntercom, Any]
    uuid: str

    class Config:
        from_attributes = True

    # if task_type == "initialize_model" check task is InitModelIntercom
    @model_validator(mode="after")
    def _validate_task(self) -> Self:
        if self.task_type == "initialize_model":
            if not isinstance(self.task, InitModelIntercom):
                raise ValueError("Task should be an InitModelIntercom object")
        return self
