from pydantic import BaseModel, field_validator
from typing import Optional, Union, List


class PolygonCoordinate(BaseModel):
    x: Union[int, float]
    y: Union[int, float]

    class Config:
        from_attributes = True


class PolygonObject(BaseModel):
    id: Optional[Union[str, int]] = None  # unique identifier of the object
    label: Optional[str] = None  # label of the object
    objectColor: Optional[str] = None  # HEX color of the object
    coordinates: List[List[Union[int, float]]] = []
    normalized: bool = False

    class Config:
        from_attributes = True

    # validate coordinates that list of list objects has 2 elements
    @field_validator("coordinates", mode="after")
    @classmethod
    def _validate_coordinates(cls, v):
        for i in v:
            if len(i) != 2:
                raise ValueError(
                    "Each coordinate in coordinates should have 2 elements"
                )
        return v


class PolygonCover(BaseModel):
    frame_number: int
    polygons: List[PolygonObject]

    class Config:
        from_attributes = True
