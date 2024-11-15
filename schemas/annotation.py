from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone


class BboxAnnotation(BaseModel):
    id: str  # unique uuid for the annotation
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    label: Optional[str] = None
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class PolygonAnnotation(BaseModel):
    id: str  # unique uuid for the annotation
    label: Optional[str] = None
    confidence: Optional[float] = None
    coordinates: List[List[float]] = []

    class Config:
        from_attributes = True

    # validate coordinates that list of list objects has 2 elements
    @classmethod
    def validate_coordinates(cls, v):
        for i in v:
            if len(i) != 2:
                raise ValueError(
                    "Each coordinate in coordinates should have 2 elements"
                )
        return v


class AnnotationMeta(BaseModel):
    annotated_at: datetime = datetime.now(
        tz=timezone.utc
    )  # annotation creation time (ISO 8601)
    annotation_model: str  # model used for annotation
    video_source: Optional[str] = None  # video source used for annotation
    frame_idx: Optional[int] = (
        None  # frame index of the annotation if annotated on a video
    )

    class Config:
        from_attributes = True

    @staticmethod
    def get_current_time():
        return datetime.now(tz=timezone.utc)


class ImageAnnotation(BaseModel):
    image_id: str
    image_path: str  # absolute path to the image
    bbox_annotations: List[BboxAnnotation] = list()
    polygon_annotations: List[PolygonAnnotation] = list()
    meta: AnnotationMeta

    class Config:
        from_attributes = True
