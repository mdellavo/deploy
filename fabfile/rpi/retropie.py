from StringIO import StringIO

from fabric.api import task
from fabric.operations import sudo, run, put
from fabric.contrib import files
from fabric.context_managers import cd

from . import base


GAMEPAD_MACS = [
    "69:01:27:27:66:04",
    "69:01:DE:5C:66:04",
]

GAMEPAD_UDEV_PATH = "/etc/udev/rules.d/10-gamepad.rules"
GAMEPAD_UDEV_RULE = 'SUBSYSTEM=="input", ATTRS{name}=="8Bitdo NES30 Pro", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"'


def setup_gamepads():
    files.append("/etc/bluetooth/main.conf", "AutoEnable=true", use_sudo=True)  # FIXME hacked
    put(StringIO(GAMEPAD_UDEV_RULE), GAMEPAD_UDEV_PATH, use_sudo=True)


def connect_gamepads():
    pass


# RetroPie/roms -> /media/ROMs (lowercase and rename genesis)
def setup_rom_mounts():
    pass


def install_retropie():
    run("rm -rf RetroPie-Setup && git clone --depth=1 https://github.com/RetroPie/RetroPie-Setup.git")
    with cd("RetroPie-Setup"):
        sudo("./retropie_setup.sh")


@task
def bootstrap(hostname):
    base.bootstrap()
    install_retropie()
