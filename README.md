# any

Build server CLI tool for getting Git repositories built as Docker images as fast as possible.

## Installation

1) Build and install the `any` CLI tool.

    ```bash
    poetry build --format wheel
    pip install dist/any-1.0.0-py3-none-any.whl
    ```

2) Log in yourself to the GitHub Docker registry.

    ```bash
    docker login ghcr.io
    ```

3) Optionally ensure your Kubernetes cluster can pull images from the GitHub Docker registry.

    ```bash
    # Create a secret for your GitHub Docker registry credentials
    kubectl create secret docker-registry ghcr \
        --docker-server=ghcr.io \
        --docker-username=<github-user> \
        --docker-password=<github-token> \
        --docker-email=<email>
    # Patch the default service account to use the secret
    kubectl patch serviceaccount default \
        -p '{"imagePullSecrets": [{"name": "ghcr"}]}'
    ```

4) Optionally install an Ingress controller into your Kubernetes cluster.

    ```bash
    # Install the NGINX Ingress controller
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.7.1/deploy/static/provider/cloud/deploy.yaml
    ```

5) Point `any` to deploy to your favorite Kubernetes cluster by setting the `ANY_KUBECONFIG` environment variable.

    ```bash
    # any defaults to KUBECONFIG when ANY_KUBECONFIG is unset
    export ANY_KUBECONFIG=~/.kube/config
    ```

## Commands

See `any --help` for more information.

## Supported Layouts

### Python Poetry

Requires a `pyproject.toml` file.

Note;
- Standard commands of `poetry export` and `poetry build` must be functional
- The built wheel must start with the Python module's name.
- The project must use a local virtualenv in .venv (using `poetry config virtualenvs.in-project true`).
