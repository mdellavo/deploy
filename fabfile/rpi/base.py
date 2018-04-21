import getpass
from StringIO import StringIO

from fabric.api import task, env
from fabric.operations import sudo, run, put, local
from fabric.contrib import files

from ..common import apt_install, change_hostname, set_timezone

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


def configure_host(hostname):
    change_hostname(hostname)
    set_timezone(TZ)
    add_mounts()
    configure_network()
    configure_kernel()


def configure_kernel(configs):
    for config in configs:
        files.append("/boot/config.txt", config, use_sudo=True)


def configure_network():
    password = getpass.getpass("Password for network: ")
    files.append("/etc/network/interfaces", WLAN_IFACE, use_sudo=True)

    config = WIFI_CONFIG.format(ssid=SSID, password=password)
    f = StringIO(config)
    put(f, "/etc/wpa_supplicant/wpa_supplicant.conf", use_sudo=True)


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
    local("ssh-copy-id marc@" + env.host_string)


def change_pi_password():
    run("passwd")


def bootstrap(hostname):
    configure_host(hostname)
    install_packages()
    add_user()


