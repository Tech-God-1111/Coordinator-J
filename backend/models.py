from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class TaskStatus(str, Enum):
    CREATED = "created"
    PLANNING = "planning"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    UNSUPPORTED = "unsupported"


@dataclass
class Task:
    request: str
    task_id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.CREATED
    selected_tool: str | None = None
    results: list[str] = field(default_factory=list)


@dataclass
class ToolResult:
    success: bool
    message: str