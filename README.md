# any

Tool to support the process of quickly building Docker images from standard project layouts.

Supports the following project layouts:

- Python Poetry

## Installation

- Add `./bin` to your `PATH`

## Usage

To build from any subdirectory of a project containing a `pyproject.toml` file:

```bash
any build
```

This will build a Docker image for your project and leave the image's tag in `dist/image_tag`.
