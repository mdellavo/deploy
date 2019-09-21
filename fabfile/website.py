import os
import boto3
import mimetypes
from boto.s3.key import Key
from fabric.api import local
from fabric.decorators import task
from fabfile.aws import deploy_stack
from fabfile.config import GDAX_TRADER_HOST, SELF_HOST, WEBSITE_STACK


SELF_STATIC_PATH = os.path.expanduser("~/Projects/marcdellavolpe.com")
SELF_BUILD_PATH = SELF_STATIC_PATH + "/_site"
GDAX_TRADER_STATIC_PATH = os.path.expanduser("~/Dropbox/Projects/GDAX/web/dist")


def deploy_website(path, bucket_name):
    client = boto3.client('s3')

    def upload(_, dirname, filenames):

        exclude = [filename for filename in filenames if filename[0] == '.']
        for filename in exclude:
            filenames.remove(filename)

        def is_file(filename):
            return os.path.isfile(os.path.join(dirname, filename))

        files = [filename for filename in filenames if is_file(filename)]
        for f in files:
            local_path = os.path.join(dirname, f)
            remote_path = local_path[len(path) + 1:]
            mimetype, _ = mimetypes.guess_type(local_path)
            print(local_path, '->', remote_path)
            with open(local_path) as contents:
                client.put_object(
                    Bucket=bucket_name,
                    Key=remote_path,
                    Body=contents,
                    ACL="public-read",
                    ContentType=mimetype or "binary/octet",
                )

    os.path.walk(path, upload, None)


@task
def deploy_website_stack():
    deploy_stack('website', WEBSITE_STACK)


@task
def deploy_website_self():
    local("jekyll build -s " + SELF_STATIC_PATH + " -d " + SELF_BUILD_PATH)
    deploy_website(SELF_BUILD_PATH, SELF_HOST)


@task
def deploy_website_gdax_trader():
    deploy_website(GDAX_TRADER_STATIC_PATH, GDAX_TRADER_HOST)


ALL = [
    deploy_website_self,
    deploy_website_gdax_trader,
]


@task
def deploy_websites():
    for deploy_site in ALL:
        deploy_site()
