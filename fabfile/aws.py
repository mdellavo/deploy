import json
from time import sleep


def existing_stacks(c):
    return [s.stack_name for s in c.describe_stacks()]


def deploy_stack(conn, name, stack):
    if name not in existing_stacks(conn):
        conn.create_stack(name, template_body=json.dumps(stack))
    else:
        conn.update_stack(name, template_body=json.dumps(stack))


def get_stack_outputs(conn, name):
    return {output.key: output.value for output in conn.describe_stacks(name)[0].outputs}


def wait_for_stack(conn, name, timeout=10):
    while True:
        rv = conn.describe_stacks(name)
        print rv[0].stack_status
        if rv[0].stack_status.endswith('_COMPLETE'):
            break
        sleep(timeout)
