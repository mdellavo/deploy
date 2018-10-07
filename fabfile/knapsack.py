import os

from fabric.api import task, put, run
from fabric.contrib.files import append, exists
from fabric.operations import sudo
from fabric.context_managers import settings
from fabric.contrib.project import rsync_project

from .website import deploy_website
from .config import KNAPSACK_WEB_HOST, CONFIGS_PATH

KNAPSACK_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "Knapsack")
KNAPSACK_WEB_PATH = os.path.join(KNAPSACK_PATH, "web", "build")
KNAPSACK_BACKEND_PATH = os.path.join(KNAPSACK_PATH, "backend")


@task
def sync_knapsack():
    sudo("mkdir -p /site/knapsack")
    rsync_project(
        remote_dir="/tmp/knapsack/",
        local_dir=KNAPSACK_BACKEND_PATH + "/*",
        exclude=[
            "*.pyc",
            ".idea",
            #"*.egg-info",
            "*.sqlite",
            "development.ini",
            "Dockerfile*",
        ],
        delete=True,
    )
    sudo("rm -rf /site/knapsack")
    sudo("mv /tmp/knapsack /site")
    sudo("chown -R knapsack:knapsack /site/knapsack")


@task
def restart_knapsack():
    sudo("/etc/init.d/knapsack reload")


@task
def deploy_knapsack():
    sync_knapsack()
    restart_knapsack()


@task
def configure_knapsack():

    with settings(warn_only=True):
        sudo("useradd -r knapsack")

        sudo("createdb knapsack", user="postgres")
        sudo("createuser knapsack", user="postgres")
        sudo("psql knapsack -c 'GRANT ALL PRIVILEGES ON DATABASE knapsack TO knapsack'", user="postgres")

    sync_knapsack()

    with settings(warn_only=True):
        sudo("virtualenv /site/venv")
        sudo("/site/venv/bin/pip install -r /site/knapsack/requirements.txt")

        sudo("mkdir -p /site/logs")
        sudo("chmod 0777 /site/logs")

    knapsack_service = os.path.join(CONFIGS_PATH, "knapsack.service")
    put(knapsack_service, "/etc/systemd/system/", use_sudo=True)

    append(
        "/etc/tmpfiles.d/knapsack.conf",
        "d /run/knapsack 0755 knapsack knapsack -",
        use_sudo=True,
    )

    sudo("systemctl enable knapsack.service")
    sudo("systemctl start knapsack.service")

    nginx_conf_src = os.path.join(CONFIGS_PATH, "nginx.knapsack.conf")
    put(nginx_conf_src, "/etc/nginx/sites-available/knapsack", use_sudo=True)
    sudo("ln -sf /etc/nginx/sites-available/knapsack /etc/nginx/sites-enabled/knapsack")

    sudo("/etc/init.d/nginx reload")


@task
def deploy_knapsack_web():
    deploy_website(KNAPSACK_WEB_PATH, KNAPSACK_WEB_HOST)


@task
def deploy_knapsack_monitor():
    script_path = os.path.join(KNAPSACK_PATH, "scripts", "check-knapsack-api.sh")

    if not exists("./check-knapsack-api.sh"):
        put(script_path, ".")
        run("chmod a+x ./check-knapsack-api.sh")

    run("touch /tmp/crontab")
    with settings(warn_only=True):
        run("crontab -l > /tmp/crontab")
    crontab = "\t".join(("*/10", "*", "*", "*", "*", "./check-knapsack-api.sh"))
    append("/tmp/crontab", crontab)
    run("crontab /tmp/crontab")


@task
def deploy():
    configure_knapsack()

