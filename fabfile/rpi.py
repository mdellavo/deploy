"""
Tasks to setup a raspberry pi running kodi

Notes https://gist.github.com/mdellavo/5fcff3d50149a58857adbd69af560a99
"""
import os
import getpass
from StringIO import StringIO

from fabric.api import task, env
from fabric.operations import sudo, run, put, local
from fabric.context_managers import cd
from fabric.contrib import files

from .common import apt_install, change_hostname, set_timezone
from .config import CONFIGS_PATH

TZ = "America/New_York"

SSID = "tube"

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
]

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

RTLSDR_BLACKLIST = """
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
"""

WLAN_IFACE = """
auto wlan0
allow-hotplug wlan0
iface wlan0 inet dhcp
    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
"""

WIFI_CONFIG = """
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
  ssid="{ssid}"
  psk="{password}"
  key_mgmt=WPA-PSK
  scan_ssid=1
}}
"""

GAMEPAD_MACS = [
    "69:01:27:27:66:04",
    "69:01:DE:5C:66:04",
]

GAMEPAD_UDEV_PATH = "/etc/udev/rules.d/10-gamepad.rules"
GAMEPAD_UDEV_RULE = 'SUBSYSTEM=="input", ATTRS{name}=="8Bitdo NES30 Pro", MODE="0666", ENV{ID_INPUT_JOYSTICK}="1"'


@task
def configure_host(hostname):
    change_hostname(hostname)
    set_timezone(TZ)
    add_mounts()
    configure_network()
    configure_kernel()


@task
def configure_kernel():
    for config in CONFIG:
        files.append("/boot/config.txt", config, use_sudo=True)


@task
def configure_network():
    password = getpass.getpass("Password for network: ")
    files.append("/etc/network/interfaces", WLAN_IFACE, use_sudo=True)

    config = WIFI_CONFIG.format(ssid=SSID, password=password)
    f = StringIO(config)
    put(f, "/etc/wpa_supplicant/wpa_supplicant.conf", use_sudo=True)


@task
def add_mounts():
    for mount_params in MOUNTS:
        mount = "\t".join(mount_params)
        files.append("/etc/fstab", mount, use_sudo=True)


@task
def install_packages():
    sudo("apt-get update")
    sudo("apt-get dist-upgrade -y")
    apt_install(PACKAGES)


@task
def install_kodi():
    apt_install(["kodi"])
    sudo("adduser  --disabled-password --disabled-login --gecos \"\" kodi", warn_only=True)
    sudo("usermod -a -G cdrom,audio,video,plugdev,users,dialout,dip,input kodi")
    put(os.path.join(CONFIGS_PATH, "kodi.service"), "/etc/systemd/system/kodi.service", use_sudo=True)
    sudo("systemctl start kodi")
    sudo("systemctl enable kodi")


@task
def setup_gamepads():
    files.append("/etc/bluetooth/main.conf", "AutoEnable=true", use_sudo=True)  # FIXME hacked
    put(StringIO(GAMEPAD_UDEV_RULE), GAMEPAD_UDEV_PATH, use_sudo=True)


@task
def connect_gamepads():
    pass


# RetroPie/roms -> /media/ROMs (lowercase and rename genesis)
@task
def setup_rom_mounts():
    pass


@task
def install_retropie():
    run("rm -rf RetroPie-Setup && git clone --depth=1 https://github.com/RetroPie/RetroPie-Setup.git")
    with cd("RetroPie-Setup"):
        sudo("./retropie_setup.sh")


@task
def install_rtl8812au():
    apt_install(["raspberrypi-kernel-headers"])
    run("rm -rf rtl8812au && git clone https://github.com/gnab/rtl8812au.git")
    with cd("rtl8812au"):
        files.sed("Makefile", "CONFIG_PLATFORM_I386_PC = y", "CONFIG_PLATFORM_I386_PC = n")
        files.sed("Makefile", "CONFIG_PLATFORM_ARM_RPI = n", "CONFIG_PLATFORM_ARM_RPI = y")
        run("make")
        sudo("make install")


@task
def install_rtlsdr():
    run("rm -rf rtl-sdr && git clone git://git.osmocom.org/rtl-sdr.git")
    with cd("rtl-sdr"):
        run("mkdir build")
        with cd("build"):
            run("cmake ../")
            run("make")
            sudo("make install")
            sudo("ldconfig")

    f = StringIO(RTLSDR_BLACKLIST)
    put(f, "/etc/modprobe.d/rtlsdr.conf", use_sudo=True)


@task
def add_user():
    sudo("adduser marc", warn_only=True)
    sudo("usermod -a -G sudo marc")
    local("ssh-copy-id marc@" + env.host_string)


@task
def change_pi_password():
    run("passwd")


@task
def install_unifi_controller():
    sudo("wget -O /etc/apt/trusted.gpg.d/unifi-repo.gpg https://dl.ubnt.com/unifi/unifi-repo.gpg")
    sudo("echo 'deb http://www.ubnt.com/downloads/unifi/debian stable ubiquiti' | tee /etc/apt/sources.list.d/100-ubnt-unifi.list")
    sudo("apt-get update")
    apt_install(["unifi"])


@task
def bootstrap(hostname):
    configure_host(hostname)
    install_packages()
    install_rtl8812au()
    install_kodi()
    install_rtlsdr()
    install_retropie()
    add_user()


