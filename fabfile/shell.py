import os
import pprint
from crypt import crypt
from getpass import getpass

import boto
from fabric.api import env, task
from fabric.contrib.files import append, exists, uncomment, sed
from fabric.operations import sudo, run
from config import SHELL_STACK, BASE_PACKAGES, USER, SHELL_HOSTNAME, QUUUX_STACK, MAIL_FORWARDS, FORWARD_TO, TZ, HOMES_DEVICE
from aws import deploy_stack, get_stack_outputs, wait_for_stack

from .common import apt_install, change_hostname, set_timezone

# TODO
# google authenticator
# postfix ssl?
# ssl everywhere

@task
def inspect(name):
    conn = boto.connect_cloudformation()

    outputs = get_stack_outputs(conn, name)
    pprint.pprint(outputs)

    env.user = "ubuntu"
    env.hosts = [outputs["PublicDNS"]]

@task
def deploy_quuux():
    conn = boto.connect_cloudformation()
    deploy_stack(conn, 'quuux', QUUUX_STACK)
    wait_for_stack(conn, 'quuux')


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
    sudo("DEBIAN_FRONTEND=noninteractive apt-get update && apt-get -y upgrade")


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
    password = getpass('Password for {}: '.format(USER))
    crypted_password = crypt(password, 'salt')
    sudo("useradd -m -G sudo -s /bin/bash -p {} {} ".format(crypted_password, USER))


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
    apt_install(["postfix"])

    append("/etc/aliases", "root:\t{}".format(FORWARD_TO.format(domain="root")), use_sudo=True)
    sudo("newaliases")

    virtual_alias_domains = "virtual_alias_domains = " + " ".join(MAIL_FORWARDS)
    append("/etc/postfix/main.cf", virtual_alias_domains, use_sudo=True)

    virtual_alias_map = "virtual_alias_maps = hash:/etc/postfix/virtual"
    append("/etc/postfix/main.cf", virtual_alias_map, use_sudo=True)

    for domain in MAIL_FORWARDS:
        forward_to = "@{} {}".format(domain, FORWARD_TO.format(domain=domain))
        append("/etc/postfix/virtual", forward_to, use_sudo=True)

    sudo("postmap /etc/postfix/virtual")
    sudo("service postfix reload")


@task
def mount_home():

    if "ext4" not in sudo("file -s " + HOMES_DEVICE):
        sudo("mkfs -t ext4 " + HOMES_DEVICE)
        sudo("mount {} -t ext4 /media".format(HOMES_DEVICE))
        sudo("rsync -aXS /home/. /media/")
        sudo("umount /media")

    append("/etc/fstab", "{}       /home   ext4    defaults,nofail        0       2".format(HOMES_DEVICE), use_sudo=True)
    sudo("mount -a")


@task
def deploy():
    set_hostname()
    update_system()
    install_ntp()
    install_postfix()
    install_apt()
    mount_home()
    add_user()
    setup_env()
    copy_ssh_id()
