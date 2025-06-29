import os
import boto3
import mimetypes
from fabric.api import local
from fabric.decorators import task
from fabfile.aws import deploy_stack
from fabfile.config import WEBSITE_STACK


SELF_STATIC_PATH = os.path.expanduser("~/Projects/marcdellavolpe.com")
SELF_BUILD_PATH = SELF_STATIC_PATH + "/_site"

FUCK_SWEENEY_STATIC_PATH = os.path.expanduser("~/Web/fucksweeney.com")
FUCK_SWEENEY_BUILD_PATH = FUCK_SWEENEY_STATIC_PATH + "/_site"

FUCK_NORCROSS_STATIC_PATH = os.path.expanduser("~/Web/fucknorcross.com")
FUCK_NORCROSS_BUILD_PATH = FUCK_NORCROSS_STATIC_PATH + "/_site"


def deploy_website(path, bucket_name):
    client = boto3.client('s3')

    for dirname, dirs, filenames in  os.walk(path):
        print("wtf", dirname, filenames)

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
                    Body=contents.read(),
                    ACL="public-read",
                    ContentType=mimetype or "binary/octet",
                )

@task
def deploy_website_stack():
    deploy_stack('website', WEBSITE_STACK)


def _build_jekyll(static_path):
    local("jekyll build -s " + static_path + " -d " + static_path + "/_site")


@task
def deploy_website_self():
    _build_jekyll(SELF_STATIC_PATH)
    deploy_website(SELF_BUILD_PATH, "marcdellavolpe.com")


ALL = [
    deploy_website_self,
]

@task
def deploy_websites():
    for deploy_site in ALL:
        deploy_site()

@task
def deploy_fuckem_both():
    _build_jekyll(FUCK_SWEENEY_STATIC_PATH)
    deploy_website(FUCK_SWEENEY_BUILD_PATH, "fucksweeney.com")
    _build_jekyll(FUCK_NORCROSS_STATIC_PATH)
    deploy_website(FUCK_NORCROSS_BUILD_PATH, "fucknorcross.com")


SAVE_AMERICA_DOMAINS = [
    "saveamericaagain.info",
    "saveamericagain.us",
    "saveamericaga.in",
    "saveamericagain.com"
]


@task
def deploy_save_america():
    pass
