from fabric.operations import sudo


def set_timezone(zoneinfo):
    sudo('cp /usr/share/zoneinfo/{} /etc/localtime'.format(zoneinfo))


def change_hostname(hosetname):
    sudo("hostname {}".format(hosetname))
    sudo("echo {} > /etc/hostname".format(hosetname))


def apt_install(packages):
    sudo("DEBIAN_FRONTEND=noninteractive apt-get install -y " + " ".join(packages))


def add_repository(url, name):
    sudo('echo "{url}" | sudo tee /etc/apt/sources.list.d/{name}.list'.format(name=name, url=url))


def apt_update():
    sudo("DEBIAN_FRONTEND=noninteractive apt-get update")


def apt_upgrade():
    apt_update()
    sudo("DEBIAN_FRONTEND=noninteractive apt-get -y upgrade")
