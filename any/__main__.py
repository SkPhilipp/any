#!/usr/bin/env python3

from any.repository import Repository
import subprocess

import fire


def default_organization_repository(organization_repository: str = None):
    if organization_repository:
        return organization_repository.split("/")
    origin_url = subprocess.check_output("git remote get-url origin", shell=True).decode("utf-8").strip()
    if origin_url.startswith("https://github.com/") and origin_url.endswith(".git"):
        return origin_url[len("https://github.com/"):][:-len(".git")].split("/")
    else:
        raise Exception(f"Could not parse GitHub organization and repository from origin URL: {origin_url}")


def default_branch(branch: str = None):
    return branch or subprocess.check_output("git rev-parse --abbrev-ref HEAD", shell=True).decode("utf-8").strip()


def default_commit(commit: str = None):
    return commit or subprocess.check_output("git rev-parse HEAD", shell=True).decode("utf-8").strip()


def any_build(organization_repository: str = None, branch: str = None, commit: str = None, tag: str = None):
    """
    - Checks out the repository to the `~/.any/` cache folder.
    - Builds the project to *.whl using Poetry through Docker, using the `~/.any/` cache folder to store the virtual environment.
    - Builds and pushes the Docker image to GitHub Packages, build is performed using the `~/.any/` cache folder's virtual environment and built *.whl.

    :param organization_repository: GitHub Organization and Repository slug, e.g. `ProductPrinter/any`
    :param branch: Git branch name
    :param commit: Git commit hash within the given branch
    :param tag: Docker image tag to use instead of the commit hash
    :return:
    """
    local_organization, local_repository = default_organization_repository(organization_repository)
    local_branch = default_branch(branch)
    local_commit = default_commit(commit)
    repository = Repository(local_organization, local_repository, local_branch, local_commit, tag)
    repository.reset()
    repository.build_poetry_artifact()
    repository.build_docker_image()


def any_deploy(organization_repository: str = None, branch: str = None, commit: str = None, tag: str = None):
    """
    - Deploys to Kubernetes, referring to the Docker image built in `any build`.

    :param organization_repository: GitHub Organization and Repository slug, e.g. `ProductPrinter/any`
    :param branch: Git branch name
    :param commit: Git commit hash within the given branch
    :param tag: Docker image tag to use instead of the commit hash
    :return:
    """
    local_organization, local_repository = default_organization_repository(organization_repository)
    local_branch = default_branch(branch)
    local_commit = default_commit(commit)
    repository = Repository(local_organization, local_repository, local_branch, local_commit, tag)
    repository.deploy()


def any_all(organization_repository: str = None, branch: str = None, commit: str = None, tag: str = None):
    """
    Equivalent to `any build` followed by `any deploy`.

    :param organization_repository: See `any build`
    :param branch: See `any build`
    :param commit: See `any build`
    :param tag: See `any build`
    :return:
    """
    local_organization, local_repository = default_organization_repository(organization_repository)
    local_branch = default_branch(branch)
    local_commit = default_commit(commit)
    repository = Repository(local_organization, local_repository, local_branch, local_commit, tag)
    repository.reset()
    repository.build_poetry_artifact()
    repository.build_docker_image()
    repository.deploy()


def main():
    fire.Fire({
        'build': any_build,
        'deploy': any_deploy,
        'all': any_all
    })


if __name__ == '__main__':
    main()
