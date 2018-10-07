from StringIO import StringIO

from fabric.api import task
from fabric.operations import sudo, put, run
from fabric.context_managers import cd

from . import base
from ..common import apt_install


RTLSDR_BLACKLIST = """
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
"""

KISMET_PACKAGES = [
    "libmicrohttpd-dev",
    "pkg-config",
    "zlib1g-dev",
    "libnl-3-dev",
    "libnl-genl-3-dev",
    "libcap-dev",
    "libpcap-dev",
    "libncurses5-dev",
    "libnm-dev",
    "libdw-dev",
    "libsqlite3-dev",
    "libprotobuf-dev",
    "libprotobuf-c-dev",
    "protobuf-compiler",
    "protobuf-c-compiler",
    "libsensors4-dev",

    "python-setuptools",
    "python-protobuf",
    "python-sqlite",
    "python-requests",

    "librtlsdr0",
]


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
def install_kismet():
    apt_install(KISMET_PACKAGES)
    run("rm -rf kismet && git clone https://www.kismetwireless.net/git/kismet.git")
    with cd("kismet"):
        run("./configure")
        run("make")
        sudo("make suidinstall")
    sudo("usermod -a -G kismet marc")


@task
def install_gpsd():
    apt_install(["gpsd", "gpsd-clients"])


@task
def bootstrap():
    base.bootstrap()
    install_rtlsdr()
    install_kismet()
    install_gpsd()
