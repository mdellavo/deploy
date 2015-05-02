import os
import pprint
from crypt import crypt
from getpass import getpass

import boto
from fabric.api import env, task
from fabric.contrib.files import append, exists, uncomment
from fabric.operations import sudo
from config import SHELL_STACK, BASE_PACKAGES, USER, SHELL_HOSTNAME, QUUUX_STACK, MAIL_FORWARDS, FORWARD_TO
from aws import deploy_stack, get_stack_outputs, wait_for_stack


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
def deploy_shell():
    conn = boto.connect_cloudformation()
    deploy_stack(conn, 'shell', SHELL_STACK)
    wait_for_stack(conn, 'shell')
    rv = get_stack_outputs(conn, 'shell')
    pprint.pprint(rv)


def sysctl(setting):
    if sudo("sysctl -w {0}".format(setting), warn_only=True).succeeded:
        append("/etc/sysctl.conf", setting, use_sudo=True)


def apt_install(packages):
    sudo("DEBIAN_FRONTEND=noninteractive apt-get install -y " + " ".join(packages))


@task
def update_system():
    sudo("DEBIAN_FRONTEND=noninteractive apt-get update && apt-get -y upgrade")


def install_ntp():
    sudo('cp /usr/share/zoneinfo/UTC /etc/localtime')
    sysctl("xen.independent_wallclock=1")
    apt_install(["ntp"])


@task
def install_apt():
    apt_install(BASE_PACKAGES)


@task
def set_hostname():
    sudo("hostname {}".format(SHELL_HOSTNAME))
    sudo("echo {} > /etc/hostname".format(SHELL_HOSTNAME))


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
def deploy():
    set_hostname()
    update_system()
    install_ntp()
    install_postfix()

    install_apt()
    add_user()
    setup_env()
    copy_ssh_id()