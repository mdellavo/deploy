#!/usr/bin/env python3
"""Assembles cloud-init.yaml from base.yaml and separate config files, then publishes to S3."""

import sys
import yaml
import boto3
from pathlib import Path

S3_BUCKET = "quuux-bootstrap"
S3_KEY    = "ralph-cloud-init.yaml"

HERE = Path(__file__).parent

# (src relative to HERE, dest on instance, owner, permissions)
FILES = [
    ("files/nginx/nginx.conf",                "/etc/nginx/nginx.conf",                          "root:root", "0644"),
    ("files/nginx/sites/quuux.org",           "/etc/nginx/sites-available/quuux.org",           "root:root", "0644"),
    ("files/nginx/sites/p.ound.town",         "/etc/nginx/sites-available/p.ound.town",         "root:root", "0644"),
    ("files/nginx/sites/liminal.quuux.org",   "/etc/nginx/sites-available/liminal.quuux.org",   "root:root", "0644"),
    ("files/nginx/sites/rogue.quuux.org",     "/etc/nginx/sites-available/rogue.quuux.org",     "root:root", "0644"),
    ("files/nginx/sites/rogue-api.quuux.org", "/etc/nginx/sites-available/rogue-api.quuux.org", "root:root", "0644"),
    ("files/postfix/main.cf",                 "/etc/postfix/main.cf",                           "root:root", "0644"),
    ("files/postfix/virtual",                 "/etc/postfix/virtual",                           "root:root", "0644"),
    ("files/postfix/aliases",                 "/etc/aliases",                                   "root:root", "0644"),
    ("files/dovecot/dovecot.conf",            "/etc/dovecot/dovecot.conf",                      "root:root", "0644"),
    ("files/inspircd/inspircd.conf",          "/etc/inspircd/inspircd.conf",                    "inspircd:inspircd", "0640"),
    ("files/docker/docker-compose.yaml",      "/opt/frink/docker-compose.yaml",                 "root:root", "0644"),
    ("files/scripts/setup-certs.sh",          "/root/setup-certs.sh",                           "root:root", "0755"),
]

STATIC_FILES = [
    ("/var/www/quuux.org/index.html",   "www-data:www-data", "0644",
     "<html>\n<head><title>quuux.org</title></head>\n<body><h1>quuux.org</h1></body>\n</html>\n"),
    ("/var/www/p.ound.town/index.html", "www-data:www-data", "0644",
     "<html>\n<head><title>p.ound.town</title></head>\n<body><h1>p.ound.town</h1></body>\n</html>\n"),
]


def main():
    config = yaml.safe_load((HERE / "base.yaml").read_text())

    write_files = []

    for src, dest, owner, perms in FILES:
        content = (HERE / src).read_text()
        write_files.append({
            "path": dest,
            "owner": owner,
            "permissions": perms,
            "content": content,
        })

    for dest, owner, perms, content in STATIC_FILES:
        write_files.append({
            "path": dest,
            "owner": owner,
            "permissions": perms,
            "content": content,
        })

    config["write_files"] = write_files

    out = "#cloud-config\n" + yaml.dump(
        config, default_flow_style=False, allow_unicode=True, sort_keys=False
    )

    out_path = HERE / "cloud-init.yaml"
    out_path.write_text(out)
    print(f"Written {out_path}", file=sys.stderr)

    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_KEY,
        Body=out.encode(),
        ContentType="text/cloud-config",
    )
    print(f"Published s3://{S3_BUCKET}/{S3_KEY}", file=sys.stderr)


if __name__ == "__main__":
    main()
