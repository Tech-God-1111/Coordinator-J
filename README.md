# Coordinator-J
## Project Overview, Setup, Usage, and Troubleshooting Guide

**Project name:** Coordinator-J  
**Application type:** Python-based task coordinator with a planned web interface  
**Current development stage:** Core coordination system; web interface integration is planned  
**Status:** Under development

---

## 1. What Is Coordinator-J?

Coordinator-J is a Python project designed to act as a central coordinator for user requests, tasks, and registered tools. Its purpose is to provide one place where requests can be received, interpreted, routed to suitable tools, and tracked through a task lifecycle.

The long-term goal is to develop Coordinator-J into a more capable assistant framework that can support intelligent planning, controlled tool execution, task tracking, and future integrations with other projects.

The existing core contains a coordinator, task models, a tool registry, and a terminal interface. A desktop interface also exists in `desktop_app.py`. The project is being prepared for a browser-based interface so that users can interact with Coordinator-J through a website instead of relying on the desktop application.

The web interface and backend must work together: the frontend presents the interface, while the Python backend processes requests and returns results.

**Important:** Coordinator-J is still under development. Its planned AI-based planning and external project integrations are not currently connected. The web interface must be configured and tested before it can be considered operational.

## 2. Project Requirements

### 2.1 Software requirements

The following software is required or expected for development:

- **Python:** A compatible Python 3 installation.
- **PyCharm or another Python editor:** Recommended for editing files and inspecting errors.
- **A modern web browser:** Required for accessing the planned browser interface.
- **Flask:** Planned for the web server if the project uses the current proposed Flask-based setup.
- **A terminal or command prompt:** Used to start the program and inspect error messages.
- **Internet connection:** May be needed to install dependencies. Normal local operation should not automatically require an internet connection unless external services or online resources are added.

The final dependency list must match the actual implementation. Do not install additional libraries unless the project requires them.

### 2.2 Hardware requirements

Coordinator-J does not currently require special hardware. A normal computer capable of running Python and a modern browser should be sufficient for basic development and local testing.

Performance requirements may increase if advanced AI models, image processing, or other computationally demanding features are introduced later.

### 2.3 Project files and folders

The planned project structure is:

    Coordinator-J/
    ├── frontend/
    │   ├── Index.html
    │   ├── Dashboard.html
    │   ├── styles.css
    │   ├── app.js
    │   └── assets/
    ├── backend/
    │   ├── coordinator.py
    │   ├── models.py
    │   ├── tools.py
    │   └── approvals.py
    ├── main.py
    ├── requirements.txt
    ├── README.md
    ├── structure.txt
    └── desktop_app.py

This is the intended organization, not proof that the web application is already configured. Existing files should be inspected before moving them. In particular, imports, file paths, and the launch process must be adjusted and tested as part of the web integration milestone.

The frontend folder contains the website files. The backend folder contains the Python coordination logic and related modules. The root-level `main.py` is intended to become the main launch point for the web application. `requirements.txt` records Python dependencies, while `README.md` documents the project.

The existing desktop interface should be retained as a backup until the browser interface has been tested successfully.

## 3. Uses and Benefits When Used Correctly

Coordinator-J is intended to provide several benefits when configured and used correctly.

### 3.1 Centralized request handling

Requests can be submitted to one central coordinator instead of requiring every tool to manage its own interaction with the user.

### 3.2 Tool organization

The tool registry provides a structured way to register tools with names, descriptions, and information about whether they change application state. This makes it easier to organize existing and future capabilities.

### 3.3 Task tracking

The task model supports task identifiers, statuses, selected tools, and result messages. These features help make task execution easier to understand and diagnose.

### 3.4 Controlled execution

Tools that change state should require explicit approval before execution. This is an important design boundary for future operations that could affect files, devices, accounts, or other systems.

### 3.5 Future expansion

The project is being designed so that more capable planning and additional integrations can be introduced gradually. Future integrations should be added only after their interfaces, permissions, and failure handling have been tested.

### 3.6 Easier interaction through a browser

The planned web interface should make Coordinator-J easier to access through a browser without depending on the Tkinter desktop window. This benefit will be available only after the frontend and backend have been connected correctly.

**Responsible use:** Do not treat a successful response from the coordinator as proof that an external operation has occurred. Verify important outcomes independently, and do not bypass approval checks for state-changing operations.

## 4. How to Use Coordinator-J

The exact interface depends on which stage of development is running.

### 4.1 Existing terminal interface

The current terminal application can be started from the project environment by running:

    python main.py

If the project uses the existing virtual environment on the development computer, the interpreter can be selected in PyCharm or invoked directly from that environment.

The existing command set includes:

- `help` — displays available commands and tools.
- `status` — requests the current project status.
- `tools` — lists registered tools.
- `history` — displays recent tasks stored during the current run.
- `exit` — exits the terminal application.

The current core supports a limited set of rule-based requests. It does not yet provide a fully connected AI planner, and the task history is stored in memory rather than being permanently saved.

### 4.2 Planned browser interface

Once the web integration has been completed and tested, the intended workflow is:

1. Open the Coordinator-J project in PyCharm.
2. Confirm that the required project files are in their intended folders.
3. Select the correct Python interpreter.
4. Install the dependencies listed in `requirements.txt`, if they are not already installed.
5. Start the web application using the configured root-level `main.py`.
6. Read the terminal output to confirm that the server started without errors.
7. Open the local address printed by the server in a browser.
8. Enter a supported request through the website.
9. Review the returned status and result.
10. Stop the local server using the method documented by the implementation when finished.

The actual browser address, available website features, and server startup command must be confirmed after the web server is implemented. Do not assume the browser interface works simply because the HTML files open in a browser; the frontend must communicate with the running backend.

## 5. How to Make the Program Work

Follow these steps in order. Complete and test one stage before moving to the next.

### Step 1: Check the project structure

Confirm that the frontend and backend folders contain the intended files. Keep a backup of the working project before moving or renaming existing modules.

### Step 2: Check the Python interpreter

In PyCharm, confirm that the project uses the intended Python environment. Using a different interpreter can cause errors such as missing modules even when those modules are installed elsewhere.

### Step 3: Check dependencies

Inspect `requirements.txt` and ensure that it lists the libraries actually used by the application. Install the listed dependencies in the selected environment, not in an unrelated Python installation.

### Step 4: Verify Python imports

The coordinator, task models, tool registry, and approval module must import correctly from their new locations. Moving files into `backend/` can break existing imports, so this must be tested before launching the web application.

### Step 5: Configure the launch point

The root-level `main.py` should start the configured web server and connect it to the coordinator. It should use the correct paths to locate the frontend files and must not start multiple servers unintentionally.

### Step 6: Start and test the server

Launch the application from PyCharm or the terminal. Confirm that startup completes without a traceback. Then open the local address reported by the server.

### Step 7: Test the interface and backend

Check that the website loads, its styling is applied, and its JavaScript runs without errors. Submit a simple supported request and verify that the backend returns the expected result.

### Step 8: Verify safety boundaries

Confirm that read-only requests behave as expected and that state-changing tools cannot execute without the required explicit approval. Do not connect external devices or systems until these checks pass.

## 6. Troubleshooting and Diagnosis

When a problem occurs, identify which layer is failing before changing code.

### Problem: Python reports that a module cannot be found

**Possible causes:** The wrong Python interpreter is selected, a dependency is missing, or moving files changed their import paths.

**Diagnosis:**
1. Check the interpreter selected in PyCharm.
2. Read the complete error message.
3. Confirm that the module exists in the expected folder.
4. Check whether the import matches the new project structure.
5. Confirm that required dependencies are installed in the selected environment.

Avoid installing random packages to solve an import error. First identify whether the missing module belongs to the project or is an external dependency.

### Problem: The web server does not start

**Possible causes:** A syntax error, a missing dependency, an incorrect import, a wrong file path, or a port conflict.

**Diagnosis:**
1. Read the terminal output from the first error onward.
2. Check the file and line number mentioned in the traceback.
3. Verify that the configured launch file exists.
4. Check that the required dependencies are installed.
5. If the error reports that the port is already in use, determine whether another instance of the application is running.

Do not assume the server started unless the terminal confirms it.

### Problem: The browser cannot open the application

**Possible causes:** The server is not running, the wrong local address was entered, or the configured port is unavailable.

**Diagnosis:**
1. Confirm that the server is still running.
2. Use the exact local address printed by the server.
3. Check the terminal for startup errors.
4. If necessary, restart the server after resolving the reported issue.

### Problem: The website loads but buttons do not work

**Possible causes:** A JavaScript error, an incorrect element reference, or a frontend request that does not match a backend route.

**Diagnosis:**
1. Open the browser's developer tools.
2. Inspect the Console for JavaScript errors.
3. Inspect the Network panel to see whether requests are being sent and what responses they receive.
4. Check that the frontend uses the correct backend endpoint.
5. Review the server terminal for corresponding errors.

### Problem: The website looks unstyled

**Possible causes:** The stylesheet path is incorrect, the CSS file is missing, or the browser cannot load the resource.

**Diagnosis:** Confirm that `styles.css` is in the expected location and that the HTML references the correct path. Inspect the browser's Network panel for missing files.

### Problem: Requests return unsupported or unexpected results

**Possible causes:** The current coordinator uses limited rule-based routing, the request does not match a supported command, or the required tool has not been registered.

**Diagnosis:** Try a known supported command such as `help` or `status`. Inspect the registered tools and the coordinator's routing logic. Remember that natural-language AI planning is not connected in the current core.

### Problem: A tool does not execute

**Possible causes:** The tool is not registered, its handler failed, or the coordinator correctly blocked an operation that changes state.

**Diagnosis:** Check the tool registry, returned task status, and error message. If the operation changes state, verify that the intended approval process is implemented and followed. Do not remove approval checks just to make the operation run.

### Problem: Task history disappears after restarting

The current history is stored in memory. It is therefore expected to be lost when the application process ends. Persistent history would require a future storage implementation.

## 7. Safe Development and Maintenance

- Keep backups before moving or editing project files.
- Change one part at a time and test it before proceeding.
- Read full error messages rather than guessing at the cause.
- Keep dependencies limited to those the application actually needs.
- Do not expose a development server to the public internet without appropriate security controls.
- Do not store passwords, API keys, or other secrets directly in source code.
- Require explicit approval for state-changing actions.
- Verify the result of important operations independently.
- Keep the desktop interface available until the web interface is stable.
- Update this README whenever the actual features, requirements, launch process, or folder structure change.

## 8. Current Limitations and Future Development

Coordinator-J is under active development. The current core provides basic rule-based request handling, a tool registry, task records, and a terminal interface. A desktop interface also exists.

The browser interface is planned, and its launch process and backend integration must be verified once implemented. AI-based planning, persistent task history, and integrations with other projects are not currently connected features.

Future development may introduce more advanced planning, persistent storage, additional tools, stronger approval workflows, and carefully controlled integrations. Each feature should be added in a separate milestone with testing before the next feature is introduced.

## 9. Final Notes

Coordinator-J is intended to grow into a modular and controlled task-coordination system. Its reliability depends on correct project organization, a working Python environment, accurate imports, tested frontend/backend communication, and clear approval boundaries.

When diagnosing an issue, begin with the simplest checks: the folder structure, Python interpreter, dependencies, imports, server output, and browser errors. Make one correction at a time and confirm the result before proceeding.

**Project principle: Build gradually, test carefully, preserve approval boundaries, and verify every important result.**
