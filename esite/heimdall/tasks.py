import json
import subprocess
from os import getenv, path

import git
from celery import Task
from celery.utils.log import get_task_logger

from esite.celery_app import app as celery_app
from .models import AsyncHeimdallGeneration

logger = get_task_logger(__name__)


class UnconfiguredEnvironment(Exception):
    """base class for new exception"""


class CallbackTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        state = "SUCCESS"
        license_key = kwargs.get("license_key")

        self.publish(
            task_id,
            state,
            license_key,
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        state = "FAILURE"
        license_key = kwargs.get("license_key")
        print(exc)
        self.publish(task_id, state, license_key)

    def publish(
        self, task_id, state, license_key, access_token=None, secure_url=None, url=None
    ):
        from .schema import OnNewHeimdallGeneration

        OnNewHeimdallGeneration.new_heimdall_generation(
            license_key=license_key,
            state=state,
            task_id=task_id,
            access_token=access_token,
            secure_url=secure_url,
            url=url,
        )


@celery_app.task(base=CallbackTask, bind=True)
def generate_bridge_drop_task(self, async_gen_id, license_key=None):
    logger.info("Generated bridge drop with heimdall")

    REMOTE_URL = getenv("GITHUB_HEIMDALL_REMOTE_URL")

    if not REMOTE_URL:
        raise UnconfiguredEnvironment(
            "GITHUB_HEIMDALL_REMOTE_URL not found in enviroment"
        )

    GENERATOR_NAME = "heimdall_generator"
    BRIDGE_DROP_NAME = "bridge-drop-1.0.0.tgz"

    if not path.exists(GENERATOR_NAME):
        repo = git.Repo.clone_from(REMOTE_URL, GENERATOR_NAME)
        print(repo)
    else:
        repo = git.Repo(GENERATOR_NAME)
        o = repo.remotes.origin
        o.pull()

    async_gen = AsyncHeimdallGeneration.objects.get(id=async_gen_id)

    subprocess.Popen(["npm", "install"], cwd=GENERATOR_NAME).wait()
    subprocess.Popen(["npm", "run", "build"], cwd=GENERATOR_NAME).wait()
    exit = subprocess.Popen(
        ["node", "lib/index.js", "", json.dumps(async_gen.introspection)],
        cwd=GENERATOR_NAME,
    ).wait()

    if exit != 0:
        raise ValueError("Generating drop failed")

    async_gen.bridge_drop_binary = open(
        f"{GENERATOR_NAME}/bridge-drop/{BRIDGE_DROP_NAME}", "rb"
    ).read()
    async_gen.bridge_drop_binary_name = BRIDGE_DROP_NAME
    async_gen.save()

    return async_gen.id
