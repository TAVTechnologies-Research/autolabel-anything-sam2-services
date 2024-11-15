from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, TypeVar, Literal, Union

from .prompt import PointPrompt, AnnotationObject, SingleFrameAnnotationObject
from .mask import MaskCover
from .frame import FrameCover
from .bbox import BboxCover
from .polygon import PolygonCover


class ResponseCover(BaseModel):
    msg_type: str
    data: Any = None
    error: Any = None
    meta: Any = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


class ErrorResponseCover(ResponseCover):
    msg_type: str = "error"
    data: None = None
    error: Dict[str, Any] = dict()
    meta: Any = None
    message: str = "An error occurred"

    class Config:
        from_attributes = True


class ResetTaskInputCover(ResponseCover):
    msg_type: str = "reset"
    data: Any = None


class PointPromptInputCover(ResponseCover):
    msg_type: str = "add_points"
    data: List[AnnotationObject] = []

    class Config:
        from_attributes = True


class SingleFramePointPromptInputCover(PointPromptInputCover):
    data: List[SingleFrameAnnotationObject] = []


class RunInferenceInputCover(PointPromptInputCover):
    msg_type: str = "run_inference"

    class Config:
        from_attributes = True


class RemoveObjectInputCover(ResponseCover):
    msg_type: str = "remove_object"
    data: List[str] = []  # list of object ids

    class Config:
        from_attributes = True


class SingleFrameMaskResponseCover(ResponseCover):
    msg_type: str = "mask"
    data: Optional[MaskCover] = None


class SingleFrameResponseCover(ResponseCover):
    msg_type: Literal["frame", "mask", "polygon", "bbox"] = "frame"
    data: Optional[Union[FrameCover, MaskCover, BboxCover, PolygonCover]] = None
    meta: Dict[str, Any] = dict()


ResponseType = TypeVar("ResponseType", bound=ResponseCover)
