set +e

SSH_OPTS="PreferredAuthentications=password -o PubkeyAuthentication=no -oHostKeyAlgorithms=+ssh-dss"

set_inform() {
    echo "set-inform http://${2}:8080/inform"
    ssh -o $SSH_OPTS admin@$1
}

CONTROLLER="192.168.1.224"

set_inform "192.168.1.1" $CONTROLLER
set_inform "192.168.1.250" $CONTROLLER
# set_inform "192.168.1.227" $CONTROLLER
