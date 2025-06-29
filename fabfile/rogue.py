import os

from fabric.api import task, local
from fabric.operations import sudo
from fabric.context_managers import settings, lcd

from .website import deploy_website


ROGUE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "rogue")
ROGUE_WEB_PATH = os.path.join(ROGUE_PATH, "web")
ROGUE_BUILD_PATH = os.path.join(ROGUE_WEB_PATH, "build")


@task
def deploy_web():
    with lcd(ROGUE_WEB_PATH):
        local("yarn build")
    deploy_website(ROGUE_BUILD_PATH, "rogue.quuux.org")
