import os
import pprint
from crypt import crypt
from getpass import getpass

import boto
from fabric.api import env, task, local, put, run
from fabric.contrib.files import append, exists, uncomment, contains, sed
from fabric.operations import sudo
from fabric.context_managers import settings
from config import SHELL_STACK, BASE_PACKAGES, USER, SHELL_HOSTNAME, MAIL_FORWARDS, FORWARD_TO, TZ, HOMES_DEVICE, DB_DEVICE, DB_PATH
from aws import deploy_stack, get_stack_outputs, wait_for_stack

from .common import apt_install, change_hostname, set_timezone, add_repository, apt_update

CONFIGS_PATH = os.path.join(os.path.dirname(__file__), "..", "config")


@task
def inspect(name):
    conn = boto.connect_cloudformation()

    outputs = get_stack_outputs(conn, name)
    pprint.pprint(outputs)

    env.user = "ubuntu"
    env.hosts = [outputs["PublicDNS"]]


@task
def deploy_shell(name="shell"):
    conn = boto.connect_cloudformation()
    deploy_stack(conn, name, SHELL_STACK)
    wait_for_stack(conn, name)
    rv = get_stack_outputs(conn, name)
    pprint.pprint(rv)


def sysctl(setting):
    if sudo("sysctl -w {0}".format(setting), warn_only=True).succeeded:
        append("/etc/sysctl.conf", setting, use_sudo=True)


@task
def update_system():
    apt_update()
    sudo("DEBIAN_FRONTEND=noninteractive apt-get -y upgrade")


@task
def setup_unattended_upgrades():
    apt_install(["unattended-upgrades"])
    sudo("DEBIAN_FRONTEND=noninteractive dpkg-reconfigure --priority=low unattended-upgrades")


@task
def install_ntp():
    set_timezone(TZ)
    sysctl("xen.independent_wallclock=1")
    apt_install(["ntp"])


@task
def install_apt():
    apt_install(BASE_PACKAGES)


@task
def set_hostname():
    change_hostname(SHELL_HOSTNAME)


@task
def add_user():
    if not contains("/etc/passwd", USER):
        password = getpass('Password for {}: '.format(USER))
        crypted_password = crypt(password, 'salt')
        sudo("useradd -m -G sudo,docker -s /bin/bash -p {} {} ".format(crypted_password, USER))

    with settings(warn_only=True):
        sudo("createuser -s -d -r {}".format(USER), user="postgres")


@task
def copy_ssh_id():
    if not exists("/home/{}/.ssh".format(USER)):
        sudo("mkdir /home/{}/.ssh".format(USER), user=USER)
        sudo("touch /home/{}/.ssh/authorized_keys".format(USER), user=USER)

    with open(os.path.expanduser("~/.ssh/id_rsa.pub")) as f:
        pub = f.read()
    append("/home/{}/.ssh/authorized_keys".format(USER), pub, use_sudo=True)


@task
def setup_env():
    uncomment("/home/{}/.bashrc".format(USER), '#force_color_prompt=yes', use_sudo=True)


@task
def install_postfix():
    apt_install(["postfix", "opendkim", "opendkim-tools"])

    sudo("echo quuux.org > /etc/mailname")

    opendkim_conf_src = os.path.join(CONFIGS_PATH, "opendkim.conf")
    put(opendkim_conf_src, "/etc/opendkim.conf", use_sudo=True)

    run("opendkim-genkey -t -s mail -d quuux.org")
    sudo("mv mail.private /etc/dkimkeys/mail.key.pem")
    sudo("chown opendkim /etc/dkimkeys/mail.key.pem")
    sudo("chmod 0600 /etc/dkimkeys/mail.key.pem")
    run("cat mail.txt")

    append("/etc/default/opendkim", "SOCKET=\"inet:8891@localhost\"", use_sudo=True)
    sudo("service opendkim restart")

    postfix_conf_src = os.path.join(CONFIGS_PATH, "postfix.conf")
    put(postfix_conf_src, "/etc/postfix/main.cf", use_sudo=True)

    append("/etc/aliases", "root:\t{}".format(FORWARD_TO.format(domain="root")), use_sudo=True)
    sudo("newaliases")

    for domain in MAIL_FORWARDS:
        forward_to = "@{} {}".format(domain, FORWARD_TO.format(domain=domain))
        append("/etc/postfix/virtual", forward_to, use_sudo=True)

    sudo("postmap /etc/postfix/virtual")
    sudo("service postfix reload")


def initialize_ebs(device, mountpoint):
    should_init = "ext4" not in sudo("file -s " + device)
    if should_init:
        sudo("mkfs -t ext4 " + device)
    if not exists(mountpoint):
        sudo("mkdir {}".format(mountpoint))
    append("/etc/fstab", "{}\t{}\text4\tdefaults,nofail\t0\t2".format(device, mountpoint), use_sudo=True)
    return should_init


@task
def initialize_volumes():

    if initialize_ebs(HOMES_DEVICE, "/home"):
        sudo("mount {} -t ext4 /media".format(HOMES_DEVICE))
        sudo("rsync -aXS /home/. /media/")
        sudo("umount /media")

    if initialize_ebs(DB_DEVICE, DB_PATH):
        sudo("chown postgres:postgres {}".format(DB_PATH))

    sudo("mount -a")


@task
def install_docker():
    # add docker
    sudo("apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D")
    add_repository("deb https://apt.dockerproject.org/repo ubuntu-xenial main", "docker")
    apt_update()
    apt_install(["docker-engine"])
    sudo("service docker start")
    sudo("systemctl enable docker")


CONTAINER_SUBNET = "172.17.0.0/16"
BRIDGE_IP = "172.17.0.1"
LISTEN_ADDRESSES = "listen_addresses = '*'"


@task
def install_postgres():
    sudo("wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -")
    add_repository("deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main", "postgres")
    apt_update()
    apt_install(["postgresql", "postgresql-contrib"])
    sudo("systemctl stop postgresql")
    sed("/etc/postgresql/9.6/main/postgresql.conf", "/var/lib/postgresql/9.6/main", "/db/postgres/main", use_sudo=True)
    if not contains("/etc/postgresql/9.6/main/pg_hba.conf", CONTAINER_SUBNET):
        append("/etc/postgresql/9.6/main/pg_hba.conf", "host\tall\tall\t{}\ttrust".format(CONTAINER_SUBNET), use_sudo=True)

    if not contains("/etc/postgresql/9.6/main/postgresql.conf", LISTEN_ADDRESSES):
        append("/etc/postgresql/9.6/main/postgresql.conf", LISTEN_ADDRESSES, use_sudo=True)
    sudo("systemctl start postgresql")


@task
def install_nginx():
    sudo("add-apt-repository ppa:nginx/stable")
    apt_update()
    apt_install(["nginx"])

    nginx_conf_src = os.path.join(CONFIGS_PATH, "nginx.snake.conf")
    put(nginx_conf_src, "/etc/nginx/sites-available/default", use_sudo=True)

    # sudo("rm /var/www/html/index.nginx-debian.html")
    # sudo("touch /var/www/html/index.html")

    sudo("/etc/init.d/nginx restart")


def deploy_container(container_id):
    path = "/tmp/{}.tar".format(container_id)
    local("docker save -o {} {}".format(path, container_id))
    put(path, path)
    sudo("docker load -i {}".format(path))

    rm = "rm {}".format(path)
    run(rm)
    local(rm)


def container_address(container_id):
    return sudo("docker inspect {}|jq -r .[].NetworkSettings.IPAddress".format(container_id))


def add_container_host(container_id):
    sudo("sed -i /{}/d /etc/hosts".format(container_id))
    append("/etc/hosts", "{}\t{}".format(container_address(container_id), container_id), use_sudo=True)


@task
def restart_knapsack():
    with settings(warn_only=True):
        sudo("/usr/bin/docker stop -t 2 knapsack")
        sudo("docker rm knapsack")

    secret = getpass()
    sudo("/usr/bin/docker run -d --tmpfs=1 --restart always --name knapsack -h knapsack --add-host database:172.17.0.1 -e LOCKBOX_SECRET={} knapsack".format(secret))


@task
def deploy_knapsack():
    deploy_container("knapsack")
    restart_knapsack()
    add_container_host("knapsack")


@task
def configure_knapsack():

    sudo("./certbot-auto certonly --nginx -m marc.dellavolpe@gmail.com --agree-tos -d knapsack-api.quuux.org")

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
def deploy_ircd():
    pass


@task
def install_letsencrypt():
    if not exists("./certbot-auto"):
        run("wget https://dl.eff.org/certbot-auto")
        run("chmod a+x ./certbot-auto")

    sudo("./certbot-auto certonly --nginx -m marc.dellavolpe@gmail.com --agree-tos -d snake.quuux.org")


@task
def deploy():
    initialize_volumes()
    set_hostname()
    update_system()
    setup_unattended_upgrades()
    install_apt()
    install_ntp()
    install_postfix()

    install_docker()
    install_postgres()
    install_letsencrypt()
    install_nginx()

    add_user()
    setup_env()
    copy_ssh_id()

    configure_knapsack()
