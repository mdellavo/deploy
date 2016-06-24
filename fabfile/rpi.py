"""
Tasks to setup a raspberry pi running kodi

Notes https://gist.github.com/mdellavo/5fcff3d50149a58857adbd69af560a99
"""
import getpass
from StringIO import StringIO

from fabric.api import task
from fabric.operations import sudo, run, put
from fabric.context_managers import cd
from fabric.contrib import files

from .common import apt_install, change_hostname, set_timezone

TZ = "America/New_York"

SSID = "tube"

PACKAGES = [
    "build-essential",
    "rpi-update",
    "git",
    "dkms",
    "kodi",
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

network={
  ssid="{ssid}"
  psk={password}
  key_mgmt=WPA-PSK
  scan_ssid=1
}
"""

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
    apt_install(PACKAGES)


@task
def install_kodi():
    files.sed("/etc/default/kodi", "ENABLED=0", "ENABLED=1")

@task
def install_kernel_source():
    sudo("rpi-update")

    run("wget https://raw.githubusercontent.com/notro/rpi-source/master/rpi-source -O /tmp/rpi-source")
    sudo("mv /tmp/rpi-source /usr/bin/rpi-source")
    sudo("chmod +x /usr/bin/rpi-source")
    run("/usr/bin/rpi-source -q --tag-update")
    run("rpi-source")


@task
def install_rtl8812au():
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
def bootstrap(hostname):
    configure_host(hostname)
    install_packages()
    install_kernel_source()
    install_rtl8812au()
    install_kodi()
    install_rtlsdr()


