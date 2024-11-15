from enum import Enum


class VideoStatus(Enum):
    READY = "ready"
    PENDING = "pending"
    PROCESSING = "processing"
    FAILED = "failed"
