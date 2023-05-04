# any

Build server tool for getting Git repositories built as Docker images as fast as possible.

## Installation

```bash
poetry build --format wheel
pip install dist/any-0.1.0-py3-none-any.whl
```

## Commands

```bash
any
```

Performs the following steps:

- Checks out the repository to the `~/.any/` cache folder.
- Builds the project to *.whl using Poetry through Docker, using the `~/.any/` cache folder to store the virtual environment.
- Builds the Docker image instantly, using the `~/.any/` cache folder's virtual environment and built *.whl.

## Supported Layouts

### Python Poetry

Requirements:

- A `pyproject.toml` file.
    - Repository folder's name must match the name defined in `pyproject.toml`.
- Standard commands of `poetry export` and `poetry build` are functional.
