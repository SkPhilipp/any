#!/usr/bin/env python3

import kopf
import logging


@kopf.on.create('installation')
def create_fn(body, **kwargs):
    # previous build code:
    # #!/usr/bin/env bash
    #
    # set -e
    # set -o pipefail
    #
    # ANY_HOME=$(any home)
    # ANY_PROJECT=$(any project)
    #
    # (
    #   # build poetry project
    #   cd "$ANY_PROJECT"
    #   rm -rf dist/*
    #   poetry build
    #   poetry export --without-hashes --without dev > dist/requirements.txt
    #
    #   # build docker image
    #   image_name=$(basename "$ANY_PROJECT")
    #   image_tag="$image_name:$(date "+%Y%m%d%H%M%S")"
    #   docker build --build-arg IMAGE_NAME="$image_name" -f "$ANY_HOME"/Dockerfile.poetry . -t "$image_tag"
    #   echo "$image_tag" > dist/image_tag
    # )
    logging.info(f"A handler is called with body: {body}")

# Operator responsibility:
#  Background:
#  - Create a buffer of N namespaces with randomly generated names.
#  - Ensure a MongoDB is deployed into each generated namespace.
#  - Ensure MongoDB credentials are available as secret $namespace/mongodb (containing “username”, “password”, “url” fields)
#  - Ensure a Deployment, Service and Ingress are deployed into each generated namespace.
#    Using an image which serves a static page returning only the namespace name.
#  On Installation:
#  - Assign the namespace to the installation entry.
#  - Update the namespace's Deployment to use the image specified in the installation.
