# any

Kubernetes Operator facilitating the quick building and deployment of projects.

## Installation

- Add `./bin/` to your `PATH`.
- Run `any install`.

Run `kopf run ./any/__main__.py --verbose` to start the operator.

## Commands

### Install

```bash
any install
```

Installs the Any operator and CRDs to a Kubernetes cluster.

### Deploy

```bash
any deploy
```

Deploys a project to a Kubernetes cluster running Any.

## Supported Layouts

### Python Poetry

Requirements:

- A `pyproject.toml` file.
  - Project folder's name must match the name defined in `pyproject.toml`.
- Standard commands of `poetry export` and `poetry build` are functional.
- Standard folder of `/dist` is used as build directory.
- Standard file format of `*.whl` is used as build artifact.
