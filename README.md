# any

Tool to support the process of quickly building Docker images from standard project layouts.

## Supported Layouts

### Python Poetry

Requirements:

- A `pyproject.toml` file.
  - Project folder's name must match the name defined in `pyproject.toml`.
- Standard commands of `poetry export` and `poetry build` are functional.
- Standard folder of `/dist` is used as build directory.
- Standard file format of `*.whl` is used as build artifact.

## Installation

Add `./bin/` to your `PATH`.

## Usage

To build a project run the following command from any directory within the project:

```bash
any build
```

This builds a Docker image containing your dependencies and build artifact.
The Docker image's tag is written to a file named `image_tag` in the associated layout's build directory.
