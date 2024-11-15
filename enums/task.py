from enum import Enum


class Task(Enum):
    INIT_MODEL = "initialize_model"
    ADD_POINTS = "add_points"
    ADD_PROMPT = "add_prompt"
    RUN_MODEL = "run_model"
    TERMINATE_MODEL = "terminate_model"
    RESET = "reset"


class TaskStatus(Enum):
    PENDING = "pending"
    STARTING = "starting"
    LOADING_VIDEO = "loading_video"
    BUSY = "busy"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    READY = "ready"
    STOPPED = "stopped"
    STOPPING = "stopping"
    UNKNOWN = "unknown"
