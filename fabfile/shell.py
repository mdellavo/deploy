import json
import pprint
from time import sleep

import boto
from fabric.api import task
from config import SHELL_STACK


def existing_stacks(c):
    return [s.stack_name for s in c.describe_stacks()]


def deploy_stack(conn, name, stack):
    if name not in existing_stacks(conn):
        conn.create_stack(name, template_body=json.dumps(stack))
    else:
        conn.update_stack(name, template_body=json.dumps(stack))


def get_stack_outputs(name):
    conn = boto.connect_cloudformation()
    return {output.key: output.value for output in conn.describe_stacks(name)[0].outputs}


@task
def deploy_shell():

    conn = boto.connect_cloudformation()

    deploy_stack(conn, 'shell', SHELL_STACK)

    while True:
        rv = conn.describe_stacks('shell')
        pprint.pprint(rv)
        sleep(5)