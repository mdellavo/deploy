"""
Tasks to setup a raspberry pi running kodi

Notes https://gist.github.com/mdellavo/5fcff3d50149a58857adbd69af560a99
"""

from fabric.api import task
from fabric.operations import sudo, run
from fabric.context_managers import cd
from fabric.contrib import files

from .common import apt_install, change_hostname

PACKAGES = [
    "build-essential",
    "rpi-update",
    "git",
    "dkms",
    "kodi",
    "ntp",
    "bc",
    "libncurses5-dev",
]

MOUNTS = [
    ("mojo:/media", "/media", "nfs", "defaults", "0", "0"),
]


def configure_kernel():
    pass


def set_timezone():
    sudo('cp /usr/share/zoneinfo/America/New_York /etc/localtime')


def add_mounts():
    for mount_params in MOUNTS:
        mount = "\t".join(mount_params)
        files.append("/etc/fstab", mount, use_sudo=True)


def set_hostname(hostname):
    change_hostname(hostname)


def install_packages():
    apt_install(PACKAGES)


def setup_kodi():
    files.sed("/etc/default/kodi", "ENABLED=0", "ENABLED=1")


def install_rtl8812au():
    sudo("rpi-update")

    run("wget https://raw.githubusercontent.com/notro/rpi-source/master/rpi-source -O /tmp/rpi-source")
    sudo("mv /tmp/rpi-source /usr/bin/rpi-source")
    sudo("chmod +x /usr/bin/rpi-source")
    run("/usr/bin/rpi-source -q --tag-update")
    run("rpi-source")

    run("git clone https://github.com/gnab/rtl8812au.git")
    with cd("rtl8812au"):
        run("make")
        sudo("make install")


@task
def bootstrap(hostname):
    configure_kernel()
    set_timezone()
    set_hostname(hostname)
    add_mounts()
    install_packages()
    install_rtl8812au()
    setup_kodi()


