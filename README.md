# any

Kubernetes Operator facilitating the quick building and deployment of repositories.

## Installation

- Add `./bin/` to your `PATH`.
- Run `any start` to create CRDs, the `any` namespace and start the operator.

## Commands

### Deploy

```bash
any deploy
```

Deploys a repository to a Kubernetes cluster running Any.

## Supported Layouts

### Python Poetry

Requirements:

- A `pyproject.toml` file.
    - Repository folder's name must match the name defined in `pyproject.toml`.
- Standard commands of `poetry export` and `poetry build` are functional.
- Standard folder of `/dist` is used as build directory.
- Standard file format of `*.whl` is used as build artifact.
