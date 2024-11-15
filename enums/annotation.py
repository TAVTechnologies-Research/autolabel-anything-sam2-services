from enum import Enum


class AnnotationStatusEnum(Enum):
    READY = "ready"  # if the annotation is ready to be processed
    IN_PROGRESS = "in_progress"  # if the annotation is being processed (while running the model on viode)
    EXPORTED = "exported"  # if the annotation has been exported
    FAILED = "failed"  # if the annotation failed to be processed
    WAITING = "waiting"  # if the annotation is waiting for the model to be ready
    UNKNOWN = "unknown"  # if the annotation status is unknown