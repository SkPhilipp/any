#!/usr/bin/env python3

from any.repository import Repository
import subprocess

import fire


class Cli(object):
    def __init__(self,
                 organization: str = None,
                 repository: str = None,
                 branch: str = None,
                 tag: str = None,
                 commit: str = None,
                 patch: str = None):
        """
        :param organization: GitHub Organization slug, e.g. `ProductPrinter`. Defaults to the current repository's organization.
        :param repository: GitHub Repository slug, e.g. `any`. Defaults to the current repository's name.
        :param branch: Git branch name. Defaults to the current repository's active branch.
        :param tag: Docker image tag to use. Defaults to the current repository's HEAD commit hash.
        :param commit: Git commit hash within the given branch. Defaults to the current repository's HEAD commit hash.
        :param patch: Path file contents to patch into the repository with before building. Defaults to the output of `git diff`.
        """
        self.organization = organization
        self.repository = repository
        self.branch = branch
        self.docker_image_version = tag
        self.commit = commit
        self.patch = patch
        self.patch_bytes = None
        self.executed = []
        self._setup()

    def _system(self, command: str):
        return subprocess.check_output(command, shell=True).decode("utf-8").strip()

    def _setup(self):
        if self.organization is None or self.repository is None:
            origin_url = self._system("git remote get-url origin")
            if not origin_url.startswith("https://github.com/") or not origin_url.endswith(".git"):
                print(f"Could not parse GitHub organization and repository from remote origin: {origin_url}")
                exit(1)
            self.organization, self.repository = origin_url[len("https://github.com/"):][:-len(".git")].split("/")
        if self.branch is None:
            self.branch = self._system("git rev-parse --abbrev-ref HEAD")
        if self.commit is None:
            self.commit = self._system("git rev-parse HEAD")
        if self.patch is None:
            self.patch_bytes = subprocess.check_output("git diff", shell=True)
        else:
            self.patch_bytes = self.patch.encode("utf-8")
        if self.docker_image_version is None:
            self.docker_image_version = self.commit

    def __str__(self):
        if self.executed:
            return f"-- Executed: {', '.join(self.executed)}"
        return ""

    def build(self):
        """
        Checks out the repository to Any's cache and builds using Poetry and Docker. Note that the Any cache directory contains both the Git repository and
         the virtual environment used by Poetry. Any Docker images built are pushed to GitHub Packages.
        """
        repository = Repository(self.organization, self.repository, self.branch, self.commit, self.docker_image_version, self.patch_bytes)
        repository.reset()
        repository.build_poetry_artifact()
        repository.build_docker_image()
        self.executed.append("build")
        return self

    def deploy(self):
        """
        Deploys an Any built Docker image to Kubernetes.
        """
        repository = Repository(self.organization, self.repository, self.branch, self.commit, self.docker_image_version, self.patch_bytes)
        repository.deploy()
        self.executed.append("deploy")
        return self


def main():
    fire.Fire(Cli)


if __name__ == '__main__':
    main()
