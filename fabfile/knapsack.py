import os
from getpass import getpass

from fabric.api import task, put, run
from fabric.contrib.files import append, exists
from fabric.operations import sudo
from fabric.context_managers import settings

from .website import deploy_website
from .config import KNAPSACK_BUCKET_NAME, CONFIGS_PATH
from .shell import deploy_container, add_container_host

KNAPSACK_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "Knapsack")
KNAPSACK_WEB_PATH = os.path.join(KNAPSACK_PATH, "web", "build")

@task
def restart_knapsack():
    with settings(warn_only=True):
        sudo("/usr/bin/docker stop -t 2 knapsack")
        sudo("docker rm knapsack")

    secret = getpass()
    sudo("/usr/bin/docker run -d --restart always --name knapsack -h knapsack --add-host database:172.17.0.1 -e LOCKBOX_SECRET={} knapsack".format(secret))


@task
def deploy_knapsack():
    deploy_container("knapsack")
    restart_knapsack()
    add_container_host("knapsack")

@task
def configure_knapsack():

    with settings(warn_only=True):
        sudo("createdb knapsack", user="postgres")
        sudo("createuser knapsack", user="postgres")
        sudo("psql knapsack -c 'GRANT ALL PRIVILEGES ON DATABASE knapsack TO knapsack'", user="postgres")

    deploy_knapsack()

    nginx_conf_src = os.path.join(CONFIGS_PATH, "nginx.knapsack.conf")
    put(nginx_conf_src, "/etc/nginx/sites-available/knapsack", use_sudo=True)
    sudo("ln -sf /etc/nginx/sites-available/knapsack /etc/nginx/sites-enabled/knapsack")

    sudo("/etc/init.d/nginx reload")

@task
def deploy_knapsack_web():
    deploy_website(KNAPSACK_WEB_PATH, KNAPSACK_BUCKET_NAME)


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

