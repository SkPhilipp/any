#!/usr/bin/env python3

from any.repository import Repository
import subprocess

import fire


def build(repository: str = None, branch: str = None, commit: str = None, tag: str = None):
    local_repository = repository or subprocess.check_output("git remote get-url origin", shell=True).decode("utf-8").strip()
    local_branch = branch or subprocess.check_output("git rev-parse --abbrev-ref HEAD", shell=True).decode("utf-8").strip()
    local_commit = commit or subprocess.check_output("git rev-parse HEAD", shell=True).decode("utf-8").strip()
    repository = Repository(local_repository, local_branch, local_commit)
    repository.reset()
    repository.build_artifact()
    repository.build_image(tag)


def main():
    fire.Fire({
        'build': build
    })


if __name__ == '__main__':
    main()
