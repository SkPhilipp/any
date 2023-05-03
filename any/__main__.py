#!/usr/bin/env python3

from kopf import cli
import kopf
import logging
import os
import subprocess
import re

ANY_CACHE = f"{os.environ['HOME']}/.any/cache"
ANY_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

os.makedirs(f"{ANY_CACHE}/repositories", exist_ok=True)
os.makedirs(f"{ANY_CACHE}/staging", exist_ok=True)


def normalize(name):
    # common protocol prefixes are removed
    replaced = re.sub(r'^https?://', '', name)
    # non a-Z 0-9 characters are replaced with _
    replaced = re.sub(r'[^a-zA-Z0-9]', '_', replaced)
    # multiple _ are replaced with single _
    replaced = re.sub(r'[_]+', '_', replaced)
    # leading _ are removed
    replaced = re.sub(r'^[_]+', '', replaced)
    # trailing _ are removed
    replaced = re.sub(r'[_]+$', '', replaced)
    # all characters are converted to lowercase
    replaced = replaced.lower()
    return replaced


def repository_id(repository, branch):
    normalized_repository = normalize(repository)
    normalized_branch = normalize(branch)
    return f"{normalized_repository}_{normalized_branch}"


def repository_directory(repository, branch):
    return f"{ANY_CACHE}/repositories/{repository_id(repository, branch)}"


def repository_reset(repository, branch, commit):
    directory = repository_directory(repository, branch)

    # don't clone already cloned repositories
    if not os.path.isdir(f"{directory}/.git"):
        os.makedirs(directory, exist_ok=True)
        os.system(f"git clone '{repository}' '{directory}'")

    # don't reset clean repositories
    if os.path.isdir(f"{directory}/dist"):
        os.system(f"git -C '{directory}' clean -fdx")

    os.system(f"git -C '{directory}' fetch")
    os.system(f"git -C '{directory}' checkout '{branch}'")
    os.system(f"git -C '{directory}' reset --hard '{commit}'")


def repository_rebuild(repository, branch, commit):
    # don't rebuild already built images
    if os.system(f"docker image inspect '{normalize(repository)}:{commit}'") == 0:
        return

    directory = repository_directory(repository, branch)
    # TODO: poetry env use 3.11

    poetry_virtualenv = subprocess.check_output(f"poetry --directory '{directory}' env info --path", shell=True).decode('utf-8').strip()
    logging.info(f"poetry_virtualenv: {poetry_virtualenv}")

    poetry_module = subprocess.check_output(f"poetry --directory '{directory}' version", shell=True).decode('utf-8').split(' ')[0].strip()
    logging.info(f"poetry_module: {poetry_module}")

    os.system(f"poetry --directory '{directory}' build --format wheel")

    image_name = normalize(repository)
    image_tag = f"{image_name}:{commit}"

    # reset out the staging directory
    os.system(f"rm -rf '{ANY_CACHE}/staging'")
    os.makedirs(f"{ANY_CACHE}/staging", exist_ok=True)

    # copy the poetry virtualenv into the staging directory
    os.system(f"cp -L -r '{poetry_virtualenv}/lib' '{ANY_CACHE}/staging/lib'")
    os.system(f"cp -L -r '{directory}/dist' '{ANY_CACHE}/staging/dist'")

    os.system(f"docker build --build-arg PYTHON_MODULE='{poetry_module}' -f '{ANY_HOME}/Dockerfile.poetry' '{ANY_CACHE}/staging' -t '{image_tag}'")


def repository_deploy(repository, branch, commit):
    # cat '{ANY_HOME}/resources/templates/namespace.yaml' | yq -y '.metadata.name = "{name}"' | kubectl apply -f -
    pass


@kopf.on.create('installation')
@kopf.on.resume('installation')
def fn_create(body, **_):
    logging.info(f"create of {body['metadata']['name']}")
    spec = body['spec']
    repository = spec['repository']
    branch = spec['branch']
    commit = spec['commit']

    logging.info(f"create of {repository} {branch} {commit}")
    repository_reset(repository, branch, commit)
    repository_rebuild(repository, branch, commit)
    repository_deploy(repository, branch, commit)


@kopf.on.update('installation')
def fn_update(spec, old, new, diff, **_):
    logging.info(f"update of {body['metadata']['name']}")
    rebuild = 'repository' in diff or 'branch' in diff or 'commit' in diff
    if not rebuild:
        return

    repository = spec['repository']
    branch = spec['branch']
    commit = spec['commit']

    repository_reset(repository, branch, commit)
    repository_rebuild(repository, branch, commit)
    repository_deploy(repository, branch, commit)
