import os
from crypt import crypt
from getpass import getpass

from fabric.api import task, put, run
from fabric.contrib.files import append, exists, uncomment, contains, sed
from fabric.operations import sudo
from fabric.context_managers import settings

from .config import SHELL_STACK, HOMES_DEVICE, DB_DEVICE, DB_PATH, CONFIGS_PATH
from .aws import deploy_stack
from .common import apt_install, change_hostname, add_repository, apt_update


USER = "marc"
SHELL_HOSTNAME = "snake.quuux.org"

BASE_PACKAGES = [
    "apt-transport-https",
    "ca-certificates",
    "curl",
    "emacs-nox",
    "build-essential",
    "python-pip",
    "python-setuptools",
    "python-dev",
    "tmux",
    "git",
    "jq",
    "mailutils",
]

MAIL_FORWARDS = [
    "quuux.org",
    "marcdellavolpe.com"
]

FORWARD_TO = "marc.dellavolpe+{domain}@gmail.com"

CERTS = [
    "knapsack-api.quuux.org",
    "snake.quuux.org",
]

@task
def push_stack(name="shell"):
    deploy_stack(name, SHELL_STACK)


def sysctl(setting):
    if sudo("sysctl -w {0}".format(setting), warn_only=True).succeeded:
        append("/etc/sysctl.conf", setting, use_sudo=True)


@task
def update_system():
    apt_update()
    sudo("DEBIAN_FRONTEND=noninteractive apt-get -y upgrade")


def setup_unattended_upgrades():
    apt_install(["unattended-upgrades"])
    sudo("DEBIAN_FRONTEND=noninteractive dpkg-reconfigure --priority=low unattended-upgrades")


def install_ntp():
    sysctl("xen.independent_wallclock=1")
    apt_install(["ntp"])


def install_apt():
    apt_install(BASE_PACKAGES)


def set_hostname():
    change_hostname(SHELL_HOSTNAME)


def add_user():
    if not contains("/etc/passwd", USER):
        password = getpass('Password for {}: '.format(USER))
        crypted_password = crypt(password, 'salt')
        sudo("useradd -m -G sudo -s /bin/bash -p {} {} ".format(crypted_password, USER))


def copy_ssh_id():
    if not exists("/home/{}/.ssh".format(USER)):
        sudo("mkdir /home/{}/.ssh".format(USER), user=USER)
        sudo("touch /home/{}/.ssh/authorized_keys".format(USER), user=USER)

    with open(os.path.expanduser("~/.ssh/id_rsa.pub")) as f:
        pub = f.read()
    append("/home/{}/.ssh/authorized_keys".format(USER), pub, use_sudo=True)


def setup_env():
    uncomment("/home/{}/.bashrc".format(USER), '#force_color_prompt=yes', use_sudo=True)


def install_certbot():
    sudo("add-apt-repository ppa:certbot/certbot")
    apt_update()
    apt_install(["python-certbot-nginx"])

    for cert in CERTS:
        sudo("certbot certonly --nginx -m marc.dellavolpe@gmail.com --agree-tos -d {}".format(cert))


@task
def update_certs():
    sudo("certbot renew --nginx -m marc.dellavolpe@gmail.com --agree-tos")


@task
def install_postfix():
    apt_install(["postfix", "opendkim", "opendkim-tools"])

    sudo("echo quuux.org > /etc/mailname")

    opendkim_conf_src = os.path.join(CONFIGS_PATH, "opendkim.conf")
    put(opendkim_conf_src, "/etc/opendkim.conf", use_sudo=True)

    run("opendkim-genkey -t -s mail -d quuux.org")
    sudo("mv mail.private /etc/dkimkeys/mail.key.pem")
    sudo("chown root:root /etc/dkimkeys/mail.key.pem")
    sudo("chmod 0600 /etc/dkimkeys/mail.key.pem")
    run("cat mail.txt")

    append("/etc/default/opendkim", "SOCKET=\"inet:8891@localhost\"", use_sudo=True)
    sudo("/lib/opendkim/opendkim.service.generate")
    sudo("systemctl daemon-reload")
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
    initialize_ebs(HOMES_DEVICE, "/home")
    initialize_ebs(DB_DEVICE, DB_PATH)
    sudo("mount -a")


@task
def install_postgres():
    sudo("wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -")
    add_repository("deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main", "postgres")
    apt_update()
    apt_install(["postgresql", "postgresql-contrib"])
    sudo("systemctl stop postgresql")

    sed("/etc/postgresql/11/main/postgresql.conf", "/var/lib/postgresql/11/main", "/db/postgres/11/main", use_sudo=True)

    sudo("systemctl start postgresql")
    with settings(warn_only=True):
        sudo("createuser -s -d -r {}".format(USER), user="postgres")


@task
def install_nginx():
    sudo("add-apt-repository ppa:nginx/stable")
    apt_update()
    apt_install(["nginx"])

    nginx_conf_src = os.path.join(CONFIGS_PATH, "nginx.snake.conf")
    put(nginx_conf_src, "/etc/nginx/sites-available/default", use_sudo=True)

    sudo("rm /var/www/html/index.nginx-debian.html")
    sudo("touch /var/www/html/index.html")

    sudo("systemctl start restart")


@task
def install_znc():
    apt_install(["znc"])


@task
def bootstrap():
    initialize_volumes()
    set_hostname()
    update_system()
    setup_unattended_upgrades()
    install_apt()
    install_ntp()

    install_postfix()
    install_znc()

    install_postgres()
    install_nginx()
    install_certbot()

    add_user()
    copy_ssh_id()
