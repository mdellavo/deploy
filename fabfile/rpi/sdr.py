from StringIO import StringIO

from fabric.api import task
from fabric.operations import sudo, put, run
from fabric.context_managers import cd

from . import base

RTLSDR_BLACKLIST = """
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
"""


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
    base.bootstrap(hostname)
    install_rtlsdr()
