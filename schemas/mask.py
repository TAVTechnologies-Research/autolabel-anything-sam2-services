from pydantic import BaseModel
from typing import List, Union, Tuple, Any


class Mask(BaseModel):
    mask_type: str = "base64"  # mask type
    id: Union[str, int]  # object id str uuid
    mask: str  # base64 encoded mask

    class Config:
        from_attributes = True


# TODO: Manage different mask types:
# - base64
# - polygon


class PolygonMask(BaseModel):
    object_id: Union[str, int]  # object id str uuid
    mask: List[Tuple[int, int]]  # list of (x, y) points

    class Config:
        from_attributes = True


class MaskCover(BaseModel):
    frame_number: int
    masks: List[Mask]

    class Config:
        from_attributes = True
