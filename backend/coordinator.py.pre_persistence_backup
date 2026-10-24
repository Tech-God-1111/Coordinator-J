
from models import Task, TaskStatus
from tools import ToolRegistry, register_default_tools


class Coordinator:
    def __init__(self):
        self.tools = ToolRegistry()
        self.tasks = {}
        register_default_tools(self.tools)

    def create_task(self, request: str) -> Task:
        task = Task(request=request)
        self.tasks[task.task_id] = task
        return task

    def plan(self, request: str):
        """Select a registered read-only tool using the local model."""
        command = request.strip().lower()

        # Keep the original exact commands as a reliable fallback.
        routes = {
            "status": "project_status",
            "check status": "project_status",
            "project status": "project_status",
            "help": "help",
        }

        if command in routes:
            return routes[command]

        # Reject clearly compound or unsupported requests conservatively.
        blocked_terms = (
            "database", "postgres", "sql", "delete", "modify",
            "edit a file", "write a file", "send an email",
            "unlock", "execute code", "run a command",
        )
        if any(term in command for term in blocked_terms):
            return None

        try:
            from model_planner import ModelPlanner

            if not hasattr(self, "_model_planner"):
                self._model_planner = ModelPlanner()

            available_tools = {
                tool.name: tool.description
                for tool in self.tools.list_tools()
                if not tool.changes_state
            }

            selected = self._model_planner.select_tool(
                request, available_tools
            )

            if selected in available_tools:
                return selected

        except Exception as exc:
            # Fail closed if model loading or inference fails.
            print(f"Model planner unavailable: {type(exc).__name__}")

        return None

    def handle_request(self, request: str) -> tuple[Task, str]:
        task = self.create_task(request)
        task.status = TaskStatus.PLANNING

        command = request.strip().lower()

        # Handle task history.
        if command == "history":
            task.status = TaskStatus.COMPLETED
            message = self.show_history()
            task.results.append(message)
            return task, message

        # List registered tools directly.
        if command == "tools":
            task.status = TaskStatus.COMPLETED

            registered_tools = self.tools.list_tools()
            lines = ["Registered tools:"]

            for tool in registered_tools:
                access = (
                    "STATE-CHANGING"
                    if tool.changes_state
                    else "READ-ONLY"
                )

                lines.append(
                    f"- {tool.name} [{access}]: "
                    f"{tool.description}"
                )

            message = "\n".join(lines)
            task.results.append(message)
            return task, message

        # Find a tool for the request.
        tool_name = self.plan(request)

        if tool_name is None:
            task.status = TaskStatus.UNSUPPORTED
            message = (
                "I don't have a tool for that request yet. "
                "No action was taken. Try 'help', 'status', "
                "or 'tools'."
            )
            task.results.append(message)
            return task, message

        tool = self.tools.get(tool_name)

        if tool is None:
            task.status = TaskStatus.FAILED
            message = f"Planned tool '{tool_name}' is not registered."
            task.results.append(message)
            return task, message

        # Safety boundary: state-changing tools need approval.
        if tool.changes_state:
            task.status = TaskStatus.FAILED
            message = (
                "Blocked: an explicit approval workflow "
                "is required before this tool can run."
            )
            task.results.append(message)
            return task, message

        task.selected_tool = tool.name
        task.status = TaskStatus.RUNNING

        try:
            result = tool.handler()
        except Exception as exc:
            task.status = TaskStatus.FAILED
            message = f"Tool execution failed: {type(exc).__name__}"
            task.results.append(message)
            return task, message

        task.results.append(result.message)

        task.status = (
            TaskStatus.COMPLETED
            if result.success
            else TaskStatus.FAILED
        )

        return task, result.message

    def show_history(self) -> str:
        if not self.tasks:
            return "No tasks recorded."

        lines = ["Recent tasks:"]

        # Show at most the latest 10 tasks, newest first.
        recent_tasks = list(self.tasks.values())[-10:]

        for task in reversed(recent_tasks):
            lines.append(
                f"- {task.request!r} | "
                f"{task.status.value} | "
                f"tool={task.selected_tool or 'none'}"
            )

        return "\n".join(lines)
