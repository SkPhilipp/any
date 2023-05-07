#!/usr/bin/env python3
import os
import re
import subprocess
import importlib.resources as pkg_resources

from any.config import Directory, ANY_KUBECONFIG


class Repository(object):
    def __init__(self, organization, repository, branch, commit, alt_image_version=None):
        """
        :param organization: GitHub Organization slug
        :param repository: GitHub Repository slug
        :param branch: Git branch name
        :param commit: Git commit hash within the given branch
        :param alt_image_version: Alternative Docker image tag version to use for any referenced images, instead of the default (the commit hash)
        """
        self.organization = organization
        self.repository = repository
        self.branch = branch
        self.commit = commit
        self.alt_image_version = alt_image_version

    def reset(self):
        print("--- resetting Git repository")
        directory_repository = Directory.repository(self.organization, self.repository)
        directory_git = os.path.join(directory_repository, ".git")

        # don't clone already cloned repositories
        if not os.path.isdir(directory_git):
            os.makedirs(directory_repository, exist_ok=True)
            os.system(f"git clone 'https://github.com/{self.organization}/{self.repository}.git' '{directory_repository}'")

        os.system(f"git -C '{directory_repository}' clean -fdx")
        os.system(f"git -C '{directory_repository}' fetch origin '{self.branch}'")
        os.system(f"git -C '{directory_repository}' reset --hard '{self.commit}'")

    def build_poetry_artifact(self):
        print("--- building artifact with Poetry")
        directory_repository = Directory.repository(self.organization, self.repository)
        directory_environment = Directory.environment(self.organization, self.repository)
        os.system(f"docker run --rm \
            --volume '{directory_repository}:/app' \
            --volume '{directory_environment}:/root/.cache/pypoetry/virtualenvs/' \
            any-build-poetry:latest")

    def _docker_image_tag(self):
        version = self.alt_image_version if self.alt_image_version else self.commit
        return f"ghcr.io/{self.organization}/{self.repository}:{version}".lower()

    def build_docker_image(self):
        print("--- building image with Docker")
        directory_project = Directory.root(self.organization, self.repository)
        image_dockerfile_generator = pkg_resources.as_file(pkg_resources.files("any.resources").joinpath("Dockerfile.image-poetry"))
        image_tag = self._docker_image_tag()
        with image_dockerfile_generator as image_dockerfile:
            os.system(f"docker build -f '{image_dockerfile}' '{directory_project}' -t '{image_tag}'")
        os.system(f"docker push {image_tag}")

    def _k8s_name(self):
        if self.branch == "master" or self.branch == "main":
            return f"{self.repository}".lower()
        raise NotImplementedError("Names dedicated to branches are not implemented at this time.")

    def deploy(self):
        print("--- deploying to Kubernetes")
        print(f"using KUBECONFIG={ANY_KUBECONFIG}")

        def wrap(command):
            return f"docker run --rm -v '{ANY_KUBECONFIG}:/.kube/config' bitnami/kubectl:1.27.1 {command}"

        k8s_name = self._k8s_name()
        docker_image_tag = self._docker_image_tag()
        dns_name = f"{self.repository}.release-engineers.com".lower()
        os.system(wrap(f"create deployment '{k8s_name}' --image='{docker_image_tag}' --port=8000 --replicas=1"))
        os.system(wrap(f"set image deployment '{k8s_name}' '*={docker_image_tag}'"))
        os.system(wrap(f"expose deployment '{k8s_name}' --port=80 --target-port=8000 --name='{k8s_name}'"))
        os.system(wrap(f"create ingress '{k8s_name}' --class=nginx --rule='{dns_name}/={k8s_name}:80'"))

    def __str__(self):
        return f"{self.organization}/{self.repository}/{self.branch}/{self.commit}"
