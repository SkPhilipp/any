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


def build(organization_repository: str = None, branch: str = None, commit: str = None, tag: str = None):
    local_organization, local_repository = default_organization_repository(organization_repository)
    local_branch = default_branch(branch)
    local_commit = default_commit(commit)
    repository = Repository(local_organization, local_repository, local_branch, local_commit, tag)
    repository.reset()
    repository.build_poetry_artifact()
    repository.build_docker_image()


def deploy(organization_repository: str = None, branch: str = None, commit: str = None, tag: str = None):
    local_organization, local_repository = default_organization_repository(organization_repository)
    local_branch = default_branch(branch)
    local_commit = default_commit(commit)
    repository = Repository(local_organization, local_repository, local_branch, local_commit, tag)
    repository.deploy()


def main():
    fire.Fire({
        'build': build,
        'deploy': deploy
    })


if __name__ == '__main__':
    main()
