#!/usr/bin/env python3

from any.repository import Repository
import kopf
import logging


@kopf.on.create('installation')
@kopf.on.resume('installation')
def fn_create(body, **_):
    logging.info(f"create of {body['metadata']['name']}")
    spec = body['spec']
    repository = spec['repository']
    branch = spec['branch']
    commit = spec['commit']

    logging.info(f"create of {repository} {branch} {commit}")
    r = Repository(repository, branch, commit)
    r.reset()
    r.build_artifact()
    r.build_image()


@kopf.on.update('installation')
def fn_update(spec, old, new, diff, **_):
    logging.info(f"update of {body['metadata']['name']}")
    rebuild = 'repository' in diff or 'branch' in diff or 'commit' in diff
    if not rebuild:
        return

    repository = spec['repository']
    branch = spec['branch']
    commit = spec['commit']

    r = Repository(repository, branch, commit)
    r.reset()
    r.build_artifact()
    r.build_image()
