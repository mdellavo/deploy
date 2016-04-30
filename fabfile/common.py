from fabric.operations import sudo


def change_hostname(hosetname):
    sudo("hostname {}".format(hosetname))
    sudo("echo {} > /etc/hostname".format(hosetname))


def apt_install(packages):
    sudo("DEBIAN_FRONTEND=noninteractive apt-get install -y " + " ".join(packages))

