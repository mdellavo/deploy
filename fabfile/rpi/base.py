from fabric.operations import sudo
from fabric.contrib import files

from ..common import apt_install


PACKAGES = [
    "build-essential",
    "rpi-update",
    "git",
    "dkms",
    "ntp",
    "bc",
    "libncurses5-dev",
    "cmake",
    "libusb-1.0-0.dev",
    "tmux",
    "lsb-release",
    "emacs-nox",
]


def add_mounts(mounts):
    for mount_params in mounts:
        mount = "\t".join(mount_params)
        files.append("/etc/fstab", mount, use_sudo=True)


def install_packages():
    sudo("apt-get update")
    sudo("apt-get dist-upgrade -y")
    apt_install(PACKAGES)


def add_user():
    sudo("adduser marc", warn_only=True)
    sudo("usermod -a -G sudo marc")


def bootstrap():
    install_packages()
    add_user()


