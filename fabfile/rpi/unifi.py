from fabric.api import task
from fabric.operations import sudo

from ..common import apt_install
from . import base

# XXX Pi hole install

def install_unifi_controller():
    sudo("wget -O /etc/apt/trusted.gpg.d/unifi-repo.gpg https://dl.ubnt.com/unifi/unifi-repo.gpg")
    sudo("echo 'deb http://www.ubnt.com/downloads/unifi/debian stable ubiquiti' | tee /etc/apt/sources.list.d/100-ubnt-unifi.list")
    sudo("apt-get update")
    apt_install(["unifi"])


@task
def bootstrap():
    base.bootstrap()
    install_unifi_controller()
