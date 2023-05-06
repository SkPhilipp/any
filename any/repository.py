#!/usr/bin/env python3
import os
import re
import subprocess
import importlib.resources as pkg_resources

from any.config import Directory


class Repository(object):
    def __init__(self, repository, branch, commit):
        self.repository = repository
        self.branch = branch
        self.commit = commit

    @staticmethod
    def _normalize(name):
        # common protocol prefixes are removed
        replaced = re.sub(r'^https?://', '', name)
        # non a-Z 0-9 characters are replaced with _
        replaced = re.sub(r'[^a-zA-Z0-9]', '_', replaced)
        # multiple _ are replaced with single _
        replaced = re.sub(r'_+', '_', replaced)
        # leading _ are removed
        replaced = re.sub(r'^_+', '', replaced)
        # trailing _ are removed
        replaced = re.sub(r'_+$', '', replaced)
        # all characters are converted to lowercase
        replaced = replaced.lower()
        return replaced

    def normalized_repository(self):
        return Repository._normalize(self.repository)

    def normalized_branch(self):
        return Repository._normalize(self.branch)

    def repository_id(self):
        return f"{self.normalized_repository()}_{self.normalized_branch()}"

    def docker_image(self):
        return f"{self.repository_id()}:{self.commit}"

    def reset(self):
        print("--- resetting Git repository")
        directory_repository = Directory.repository(self.repository_id())
        directory_git = os.path.join(directory_repository, ".git")

        # don't clone already cloned repositories
        if not os.path.isdir(directory_git):
            os.makedirs(directory_repository, exist_ok=True)
            os.system(f"git clone '{self.repository}' '{directory_repository}'")

        os.system(f"git -C '{directory_repository}' clean -fdx")
        os.system(f"git -C '{directory_repository}' fetch origin '{self.branch}'")
        os.system(f"git -C '{directory_repository}' reset --hard '{self.commit}'")

    def build_artifact(self):
        print("--- building Python artifact")
        directory_repository = Directory.repository(self.repository_id())
        directory_environment = Directory.environment(self.repository_id())
        os.system(f"docker run --rm \
            --volume '{directory_repository}:/app' \
            --volume '{directory_environment}:/root/.cache/pypoetry/virtualenvs/' \
            any-build-poetry:latest")

    def build_image(self, additional_tag):
        print("--- building Docker image")
        directory_project = Directory.project(self.repository_id())
        image_dockerfile_generator = pkg_resources.as_file(pkg_resources.files("any.resources").joinpath("Dockerfile.image-poetry"))
        with image_dockerfile_generator as image_dockerfile:
            tags = [self.docker_image()]
            if additional_tag:
                tags.append(additional_tag)
            tags = " ".join([f"-t '{tag}'" for tag in tags])
            os.system(f"docker build -f '{image_dockerfile}' '{directory_project}' {tags}")

    def __str__(self):
        return f"{self.repository}({self.branch}@{self.commit})"
