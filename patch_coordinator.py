from pathlib import Path

path = Path("backend/coordinator.py")
source = path.read_text(encoding="utf-8")

old = '''    def plan(self, request: str):
        """Simple rule-based planner. No AI model connected yet."""
        command = request.strip().lower()

        routes = {
            "status": "project_status",
            "check status": "project_status",
            "project status": "project_status",
            "help": "help",
        }

        return routes.get(command)
'''

new = '''    def plan(self, request: str):
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
'''

if old not in source:
    raise SystemExit("Expected plan() method was not found; no changes made.")

path.write_text(source.replace(old, new, 1), encoding="utf-8")
print("Updated only Coordinator.plan().")
