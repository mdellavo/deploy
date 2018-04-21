import os

from fabric.api import task
from fabric.operations import sudo, put, run
from fabric.context_managers import cd
from fabric.contrib import files

from . import base
from ..common import apt_install
from ..config import CONFIGS_PATH

MOUNTS = [
    ("mojo:/media", "/media", "nfs", "defaults",  "0", "0"),
]

CONFIG = [
    "hdmi_force_hotplug=1",
    "config_hdmi_boost=4",
    "disable_overscan=1",
    "gpu_mem=256",
    "gpu_mem_256=128",
    "gpu_mem_512=256",
    "gpu_mem_1024=256",
    "overscan_scale=1",
]

def install_rtl8812au():
    apt_install(["raspberrypi-kernel-headers"])
    run("rm -rf rtl8812au && git clone https://github.com/gnab/rtl8812au.git")
    with cd("rtl8812au"):
        files.sed("Makefile", "CONFIG_PLATFORM_I386_PC = y", "CONFIG_PLATFORM_I386_PC = n")
        files.sed("Makefile", "CONFIG_PLATFORM_ARM_RPI = n", "CONFIG_PLATFORM_ARM_RPI = y")
        run("make")
        sudo("make install")


def install_kodi():
    apt_install(["kodi"])
    sudo("adduser  --disabled-password --disabled-login --gecos \"\" kodi", warn_only=True)
    sudo("usermod -a -G cdrom,audio,video,plugdev,users,dialout,dip,input kodi")
    put(os.path.join(CONFIGS_PATH, "kodi.service"), "/etc/systemd/system/kodi.service", use_sudo=True)
    sudo("systemctl start kodi")
    sudo("systemctl enable kodi")


@task
def bootstrap(hostname):
    base.bootstrap(hostname)
    install_rtl8812au()
    install_kodi()
