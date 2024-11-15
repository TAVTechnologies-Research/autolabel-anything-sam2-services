import pathlib
from pydantic import BaseModel

from typing import Union
from datetime import datetime


class FileOut(BaseModel):
    file_name: str
    file_path: Union[str, pathlib.Path]
    file_size: int  # in bytes
    created_at: datetime

    class Config:
        from_attributes = True
