#!/usr/bin/env python3

from any.repository import Repository
import subprocess


def main():
    local_repository = subprocess.check_output("git remote get-url origin", shell=True).decode("utf-8").strip()
    local_branch = subprocess.check_output("git rev-parse --abbrev-ref HEAD", shell=True).decode("utf-8").strip()
    local_commit = subprocess.check_output("git rev-parse HEAD", shell=True).decode("utf-8").strip()
    repository = Repository(local_repository, local_branch, local_commit)
    repository.reset()
    repository.build_artifact()
    repository.build_image()


if __name__ == "__main__":
    main()
