from coordinator import Coordinator


def main():
    jarvis = Coordinator()

    print("=" * 42)
    print("          COORDINATOR-J")
    print("       Independent Agent Core")
    print("=" * 42)
    print("Type 'help' to see available commands.")

    while True:
        try:
            request = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCoordinator-J shutting down.")
            break

        if request.lower() == "exit":
            print("Coordinator-J shutting down.")
            break

        if not request:
            continue

        task, message = jarvis.handle_request(request)

        print(f"\nTask ID: {task.task_id}")
        print(f"Status:  {task.status.value}")
        if task.selected_tool:
            print(f"Tool:    {task.selected_tool}")
        print(f"JARVIS:  {message}")


if __name__ == "__main__":
    main()