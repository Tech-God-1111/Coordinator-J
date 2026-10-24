import sys
sys.path.insert(0, "backend")

from coordinator import Coordinator

c = Coordinator()

tests = [
    "status",
    "Can you help me understand the available commands?",
    "Connect to a PostgreSQL database and query its tables",
]

for request in tests:
    task, message = c.handle_request(request)
    print(f"\nRequest: {request}")
    print(f"Status: {task.status.value}")
    print(f"Selected tool: {task.selected_tool}")
    print(f"Message: {message[:160]}")
