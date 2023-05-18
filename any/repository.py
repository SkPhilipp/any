#!/usr/bin/env python3
import os
import re
import subprocess
import importlib.resources as pkg_resources

from any.config import Directory, ANY_KUBECONFIG


class Repository(object):
    def __init__(self, organization, repository, branch, commit, image_version, patch_bytes):
        """
        :param organization: GitHub Organization slug
        :param repository: GitHub Repository slug
        :param branch: Git branch name
        :param commit: Git commit hash within the given branch
        :param image_version: Docker image tag version
        :param patch: Path file contents to patch into the repository with before building
        """
        self.organization = organization
        self.repository = repository
        self.branch = branch
        self.commit = commit
        self.docker_image_version = image_version
        self.patch_bytes = patch_bytes

    def reset(self):
        print("--- resetting Git repository")
        directory = Directory.root(self.organization, self.repository)
        directory_git = os.path.join(directory, ".git")

        # don't clone already cloned repositories
        if not os.path.isdir(directory_git):
            os.makedirs(directory, exist_ok=True)
            os.system(f"git clone 'https://github.com/{self.organization}/{self.repository}.git' '{directory}'")

        os.system(f"git -C '{directory}' clean -fdx -e '.venv'")

        # don't fetch if the commit is already in the repository
        if subprocess.check_output(f"git -C '{directory}' cat-file -t '{self.commit}'", shell=True).decode("utf-8").strip() != "commit":
            os.system(f"git -C '{directory}' fetch origin '{self.branch}'")

        os.system(f"git -C '{directory}' reset --hard '{self.commit}'")
        subprocess.run(f"git apply --allow-empty", input=self.patch_bytes, shell=True, check=True, cwd=directory)

    def build_poetry_artifact(self):
        print("--- building artifact with Poetry")
        directory = Directory.root(self.organization, self.repository)
        os.system(f"docker run --rm --volume '{directory}:/app' any-build-poetry:latest")

    def _docker_image_tag(self):
        return f"ghcr.io/{self.organization}/{self.repository}:{self.docker_image_version}".lower()

    def build_docker_image(self):
        print("--- building image with Docker")
        directory = Directory.root(self.organization, self.repository)
        image_dockerfile_generator = pkg_resources.as_file(pkg_resources.files("any.resources").joinpath("Dockerfile.image-poetry"))
        image_tag = self._docker_image_tag()
        with image_dockerfile_generator as image_dockerfile:
            os.system(f"docker build --file '{image_dockerfile}' --tag '{image_tag}' '{directory}'")
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
        os.system(wrap(f"create configmap '{k8s_name}' --from-literal='DNS_NAME={dns_name}'"))
        os.system(wrap(f"create deployment '{k8s_name}' --image='{docker_image_tag}' --port=8000 --replicas=1"))
        os.system(wrap(f"set image deployment '{k8s_name}' '*={docker_image_tag}'"))
        os.system(wrap(f"set env deployment '{k8s_name}' --from=configmap/{k8s_name}"))
        os.system(wrap(f"expose deployment '{k8s_name}' --port=80 --target-port=8000 --name='{k8s_name}'"))
        os.system(wrap(f"create ingress '{k8s_name}' --class=nginx --rule='{dns_name}/={k8s_name}:80'"))

    def __str__(self):
        return f"{self.organization}/{self.repository}/{self.branch}/{self.commit}"
