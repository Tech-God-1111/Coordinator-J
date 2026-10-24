from dataclasses import dataclass
from typing import Callable

from models import ToolResult


@dataclass
class Tool:
    name: str
    description: str
    changes_state: bool
    handler: Callable[[], ToolResult]


class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, tool: Tool):
        if tool.name in self._tools:
            raise ValueError(f"Duplicate tool: {tool.name}")

        self._tools[tool.name] = tool

    def get(self, name: str):
        return self._tools.get(name)

    def list_tools(self):
        return list(self._tools.values())


def register_default_tools(registry: ToolRegistry):
    registry.register(
        Tool(
            name="project_status",
            description="Show Coordinator-J development status.",
            changes_state=False,
            handler=lambda: ToolResult(
                True,
                "Coordinator-J core is running. "
                "AI planner: connected. "
                "SmartDoor: not connected."
            ),
        )
    )

    registry.register(
        Tool(
            name="help",
            description="List supported commands and tools.",
            changes_state=False,
            handler=lambda: ToolResult(
                True,
                "Commands: help, status, tools, history, exit. "
                "Natural-language tool selection is enabled for registered tools."
            ),
        )
    )
