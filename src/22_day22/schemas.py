from enum import Enum
from typing import Any

from pydantic import BaseModel


class TaskStatus(str, Enum):
    staging = 'staging'
    running = 'running'
    notOK = 'notOK'
    finished = 'finished'


class Task(BaseModel):
    id: str
    cmd: str
    cp: Any
    status: TaskStatus = TaskStatus.staging
