# vtherm_api

The API of the Versatile Thermostat integration for Home Assistant.

## Requirements

- Python 3.14 or newer
- `pip` for local installation
- VS Code Dev Containers extension for containerized development

## Project layout

```text
.
├── .devcontainer/
├── src/
│   └── vtherm_api/
└── tests/
```

## Local development

Install the project in editable mode with development tools:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
pytest
```

## Dev Container

The repository includes a devcontainer based on the official `mcr.microsoft.com/devcontainers/python:3.14-bookworm` image.

When the container is created, VS Code runs:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

At each container start, VS Code runs:

```bash
python -m pip install -r requirements-dev.txt
```

To use it in VS Code:

1. Open the repository.
2. Run `Dev Containers: Reopen in Container`.
3. Wait for the post-create step to complete.
4. Run `pytest` inside the container.

## Tooling

- `pytest` for tests
- `ruff` for formatting and lint-oriented editing in VS Code
