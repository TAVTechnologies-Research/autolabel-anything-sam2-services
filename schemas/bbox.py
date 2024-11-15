from pydantic import BaseModel
from typing import Union, Optional


class BboxObject(BaseModel):
    id: Optional[Union[str, int]] = None  # unique identifier of the object
    label: Optional[str] = None  # label of the object
    objecColor: Optional[str] = None  # HEX color of the object
    xmin: Union[int, float]
    ymin: Union[int, float]
    xmax: Union[int, float]
    ymax: Union[int, float]
    normalized: bool = False

    class Config:
        from_attributes = True


class BboxCover(BaseModel):
    frame_number: int
    bboxes: list[BboxObject]

    class Config:
        from_attributes = True
