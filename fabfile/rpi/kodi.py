import os

from fabric.api import task
from fabric.operations import sudo, put

from ..common import apt_install
from ..config import CONFIGS_PATH
from . import base

MOUNTS = [
    ("mojo:/media", "/media", "nfs", "defaults",  "0", "0"),
]


def install_kodi():
    apt_install(["kodi"])
    sudo("adduser  --disabled-password --disabled-login --gecos \"\" kodi", warn_only=True)
    sudo("usermod -a -G cdrom,audio,video,plugdev,users,dialout,dip,input kodi")
    put(os.path.join(CONFIGS_PATH, "kodi.service"), "/etc/systemd/system/kodi.service", use_sudo=True)
    sudo("systemctl start kodi")
    sudo("systemctl enable kodi")


@task
def bootstrap():
    base.bootstrap()
    base.add_mounts(MOUNTS)
    install_kodi()
