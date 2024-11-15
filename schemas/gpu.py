from __future__ import annotations
from pydantic import BaseModel
from typing import Union
from typing_extensions import Self


class GPUStats(BaseModel):
    gpu_name: str
    total_memory: Union[int, float]
    free_memory: Union[int, float]
    used_memory: Union[int, float]

    class Config:
        from_attributes = True

    def to_gib(
        self,
    ) -> GPUStats:
        self.total_memory = round(self.total_memory / 1024**3, 3)
        self.free_memory = round(self.free_memory / 1024**3, 3)
        self.used_memory = round(self.used_memory / 1024**3, 3)
        return self
