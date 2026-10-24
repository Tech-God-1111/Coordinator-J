
from backend.model_planner import ModelPlanner


TOOLS = {
    "project_status": "Show Coordinator-J development status.",
    "help": "List supported commands and tools.",
}

planner = ModelPlanner()

tests = [
    (
        "Show me Coordinator-J's development status.",
        "project_status",
    ),
    (
        "Help me understand the available commands.",
        "help",
    ),
    (
        "Connect to a PostgreSQL database and query its tables.",
        None,
    ),
]

passed = 0

for request, expected in tests:
    actual = planner.select_tool(request, TOOLS)
    success = actual == expected
    passed += int(success)

    print(f"\nRequest:  {request}")
    print(f"Expected: {expected!r}")
    print(f"Actual:   {actual!r}")
    print(f"Result:   {'PASS' if success else 'FAIL'}")

print(f"\nSummary: {passed}/{len(tests)} tests passed.")
