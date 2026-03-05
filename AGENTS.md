# AGENTS.md - Guidelines for AI Agents

This document provides guidelines for AI coding agents working in this repository.

## Project Overview

This is a cross-platform Python + Tkinter desktop application for managing Docker Compose containers. The app provides a simple UI to control a docker-compose project with Start/Stop/Reload/Nuke operations and folder selection for volume mounting.

## Directory Structure

```
/workspace/
├── .env                 # Environment variables (gitignored)
├── .env.sample         # Template for .env
├── docker-compose.yml   # Docker compose configuration
├── Dockerfile          # Container definition
├── requirements.txt    # Runtime dependencies (usually empty - stdlib only)
├── requirements-dev.txt # Development dependencies (pytest, ruff)
├── ui/                 # Python application
│   ├── main.py         # Main application entry point
│   └── test_main.py   # Unit tests
└── workspace/          # Default workspace folder
```

## Build/Lint/Test Commands

### Running Tests

```bash
# Run all tests
python3 -m pytest

# Run all tests with verbose output
python3 -m pytest -v

# Run a single test
python3 -m pytest ui/test_main.py::TestDockerManagerApp::test_start_session_container_not_built

# Run tests matching a pattern
python3 -m pytest -k "start_session"
```

### Code Quality

```bash
# Format code with ruff
ruff format

# Lint with ruff
ruff check

# Fix auto-fixable issues
ruff check --fix
```

### Running the Application

```bash
# Run the UI application
python3 ui/main.py
```

## Code Style Guidelines

### General Principles

- Keep code minimal and simple - avoid over-engineering
- Prefer explicit over implicit
- Write code that is easy to understand and maintain
- Avoid premature abstraction

### Imports

- Standard library imports first, then third-party
- Use absolute imports (e.g., `from ui.main import ...`)
- Group: stdlib → third-party → local
- No wildcard imports (`from x import *`)

```python
# Correct
import os
import subprocess
import tkinter as tk
import tkinter.filedialog as filedialog
from pathlib import Path

# Incorrect
from os import *
import sys, json
```

### Formatting

- Use **ruff format** for automatic formatting
- Maximum line length: 88 characters (ruff default)
- Use 4 spaces for indentation (no tabs)
- One blank line between top-level definitions
- No trailing whitespace

### Type Hints

- Always use type hints for function signatures
- Use built-in types directly (`str`, `int`, `list`, `dict`)
- Use `typing` module for complex types: `dict[str, str]`, `list[int]`, `Optional[str]`
- Avoid `Any` unless absolutely necessary

```python
# Correct
def _read_env_file(self) -> dict[str, str]:
    env_values: dict[str, str] = {}
    ...

# Avoid
def _read_env_file(self) -> dict:
    env_values = {}
    ...
```

### Naming Conventions

- **Variables/functions**: snake_case (`selected_folder`, `_run_docker_command`)
- **Classes**: PascalCase (`DockerManagerApp`)
- **Constants**: UPPER_SNAKE_CASE (`ROOT_DIR`, `ENV_FILE`)
- **Private methods**: prefix with underscore (`_setup_ui`, `_check_docker`)
- Be descriptive but concise: `_is_container_built` not `_check_if_container_is_built`

### Error Handling

- Use specific exception types (`FileNotFoundError`, `subprocess.TimeoutExpired`)
- Always update the status bar on errors
- Return `False` from functions that can fail, let caller decide handling
- Never swallow exceptions silently without logging

```python
# Correct
try:
    result = subprocess.run(...)
    if result.returncode == 0:
        return True
    else:
        self._update_status(f"Error: {error_msg}", error=True)
        return False
except subprocess.TimeoutExpired:
    self._update_status("Error: Command timed out", error=True)
    return False
except FileNotFoundError:
    self._update_status("Error: docker not found", error=True)
    return False
```

### File Paths

- Use `os.path` for cross-platform path handling
- Never hardcode absolute paths
- Use `os.path.join()` for path concatenation
- Use `os.path.normpath()` to normalize paths

```python
# Correct
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))

# Incorrect
ROOT_DIR = "/workspace/"  # Not portable
ROOT_DIR = "C:\\workspace\\"  # Windows-specific
```

### Testing Guidelines

- Use `unittest` framework with `unittest.mock`
- Mock `subprocess.run` to avoid actual docker commands
- Mock `tk.Tk` to avoid GUI initialization in tests
- Use clear, descriptive test names: `test_<method>_<expected_behavior>`
- Test file naming: `<module>_test.py` or `test_<module>.py`

```python
@patch("ui.main.subprocess.run")
def test_start_session_container_not_built(self, mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    self.app._is_container_built = MagicMock(return_value=False)
    self.app._start_session()
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    self.assertEqual(args[0], "docker-compose")
```

### Tkinter-Specific

- Use `tkinter.filedialog` imported explicitly: `import tkinter.filedialog as filedialog`
- Avoid Windows-specific color names like `SystemFace` - use `lightgray` instead
- Use `state="readonly"` for read-only Entry widgets
- Always call `root.update()` before blocking operations to refresh UI

### Docker Commands

- All docker commands run from `ROOT_DIR` (project root)
- Use `docker compose` (space) not `docker-compose` (hyphen) for modern Docker
- Use `docker-compose` (hyphen) only when building for the first time
- Commands always use `-d` (detached mode) for `up`

## Configuration

- Use `.env` file for configuration (NOT config.json)
- Read `WORKSPACE_SOURCE` from `.env` for mount path
- Create `.env` from `.env.sample` on first run if missing
- Never commit `.env` - it's in `.gitignore`

## Dependencies

- **Runtime**: Only stdlib modules (tkinter, subprocess, os, shutil, etc.)
- **Development**: pytest, ruff
- Add runtime deps to `requirements.txt`
- Add dev deps to `requirements-dev.txt`

## Git Workflow

- Never commit `.env`, `__pycache__/`, `.ruff_cache/`, `.pytest_cache/`
- Run `ruff format` and `ruff check` before committing
- Ensure all tests pass before committing
