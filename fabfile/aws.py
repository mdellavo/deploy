import json
import time

from .config import REGION

import boto3


def existing_stacks(c):
    return [s["StackName"] for s in c.describe_stacks()["Stacks"]]


def deploy_stack(name, stack):
    client = boto3.client('cloudformation', region_name=REGION)

    if name not in existing_stacks(client):
        client.create_stack(StackName=name, TemplateBody=json.dumps(stack))
    else:
        client.create_change_set(StackName=name, TemplateBody=json.dumps(stack), ChangeSetName=name + "-" + str(int(time.time())))
