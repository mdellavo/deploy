import os
from io import StringIO

from fabric.api import task, put
from fabric.contrib.files import append
from fabric.operations import sudo, run

from .config import SHELL_STACK, CONFIGS_PATH
from .aws import deploy_stack

PACKAGES = [
    "man-db",
    "logrotate",
    "vim",
    "sudo",
    "bash-completion",
    "tmux",
    "ntp",
    "wget",
    "curl",
    "emacs-nox",
    "base-devel",
    "tmux",
    "git",
    "jq",
    "mailutils",
    "nginx",
    "certbot",
    "certbot-nginx",
    # "postfix",
    "tailscale",
    "openssl",
    "bpytop",
    "tree",
    "strace",
    "gdb",
    "htop",
    "dnsutils",
]

MAIL_FORWARDS = [
    "quuux.org",
    "marcdellavolpe.com"
]

FORWARD_TO = "marc.dellavolpe+{domain}@gmail.com"

CERTS = [
    "quuux.org",
    "snake.quuux.org",
    "frink.quuux.org",
    "atomic.quuux.org",
    "homephone.quuux.org",
    "liminal.quuux.org",
    "rogue.quuux.org",
    "rogue-api.quuux.org",
    "p.ound.town",
]

@task
def push_stack(name="shell"):
    deploy_stack(name, SHELL_STACK)


@task
def install_packages():
    sudo("pacman -S " + " ".join(PACKAGES))

@task
def update_packages():
    sudo("pacman -Sy archlinux-keyring && pacman -Syu")


@task
def request_certs():
    for cert in CERTS:
        sudo("certbot run --nginx -m marc.dellavolpe@gmail.com --agree-tos -d {}".format(cert))

@task
def update_certs():
    sudo("certbot renew --nginx -m marc.dellavolpe@gmail.com --agree-tos")


@task
def configure_postfix():
    sudo("echo quuux.org > /etc/mailname")

    postfix_conf_src = os.path.join(CONFIGS_PATH, "postfix.conf")
    put(postfix_conf_src, "/etc/postfix/main.cf", use_sudo=True)

    append("/etc/aliases", "root:\t{}".format(FORWARD_TO.format(domain="root")), use_sudo=True)
    sudo("newaliases")

    for domain in MAIL_FORWARDS:
        forward_to = "@{} {}".format(domain, FORWARD_TO.format(domain=domain))
        append("/etc/postfix/virtual", forward_to, use_sudo=True)

    sudo("postmap /etc/postfix/virtual")
    sudo("systemctl restart postfix")


NGINX_HOSTED_SITE_CONFIG = """
server {{
    listen 443 ssl;

    server_name {NAME};
    root /var/www/{NAME};
    index index.html;

    ssl_certificate /etc/letsencrypt/live/{NAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{NAME}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {{
        try_files $uri $uri/ =404;
    }}

    {LOCATIONS}
}}

server {{
    listen 80;
    server_name {NAME};

    if ($host = {NAME}) {{
        return 301 https://$host$request_uri;
    }}

    return 404;
}}
"""

NGINX_PROMETHEUS_METRICS_LOCATIONS = """
    location /status {
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/metrics-htpasswd;
        stub_status;
    }

    location /metrics/node {
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/metrics-htpasswd;
        proxy_pass http://localhost:9100/metrics;
    }

    location /metrics/nginx {
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/metrics-htpasswd;
        proxy_pass http://localhost:4040/metrics;
    }

    location /metrics/synapse {
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/metrics-htpasswd;
        proxy_pass http://localhost:9000/_synapse/metrics;
    }

"""

NGINX_SYNAPSE_LOCATIONS = """
    listen 8448 ssl http2 default_server;
    listen [::]:8448 ssl http2 default_server;

    location /.well-known/matrix/server {
        default_type application/json;
        return 200 '{"m.server": "p.ound.town:443"}';
	}

    location /.well-known/matrix/client {
		default_type application/json;
        return 200 '{"m.homeserver":{"base_url": "https://p.ound.town"}}';
	}

    location ~ ^(/_matrix|/_synapse/client) {
        # note: do not add a path (even a single /) after the port in `proxy_pass`,
        # otherwise nginx will canonicalise the URI and cause signature verification
        # errors.
        proxy_pass http://localhost:8008;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;

        # Nginx by default only allows file uploads up to 1M in size
        # Increase client_max_body_size to match max_upload_size defined in homeserver.yaml
        client_max_body_size 50M;
    }
"""

NGINX_PROXY_PASS_NOAUTH_CONFIG = """
server {{
    listen 443 ssl;
    server_name {NAME};

    ssl_certificate /etc/letsencrypt/live/{NAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{NAME}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {{
        proxy_pass {TARGET};
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
        proxy_request_buffering off;
    }}
}}

server {{
    listen 80;
    server_name {NAME};

    if ($host = {NAME}) {{
        return 301 https://$host$request_uri;
    }}

    return 404;
}}
"""


NGINX_PROXY_PASS_SITE_CONFIG = """
server {{
    listen 443 ssl;
    server_name {NAME};

    ssl_certificate /etc/letsencrypt/live/{NAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{NAME}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    auth_basic "Are you elite?";
    auth_basic_user_file /etc/nginx/htpasswd;

    location / {{
        proxy_pass {TARGET};
    }}
}}

server {{
    listen 80;
    server_name {NAME};

    if ($host = {NAME}) {{
        return 301 https://$host$request_uri;
    }}

    return 404;
}}
"""

NGINX_S3_PROXY_SITE_CONFIG = """
server {{
    listen 443 ssl;
    server_name {NAME};

    ssl_certificate /etc/letsencrypt/live/{NAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{NAME}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {{
      proxy_http_version     1.1;
      proxy_set_header       Connection "";
      proxy_set_header       Authorization '';
      proxy_set_header       Host {BUCKET}.s3-website-us-east-1.amazonaws.com;
      proxy_hide_header      x-amz-id-2;
      proxy_hide_header      x-amz-request-id;
      proxy_hide_header      x-amz-meta-server-side-encryption;
      proxy_hide_header      x-amz-server-side-encryption;
      proxy_hide_header      Set-Cookie;
      proxy_ignore_headers   Set-Cookie;
      proxy_cache_revalidate on;
      proxy_intercept_errors on;
      proxy_pass             http://{BUCKET}.s3-website-us-east-1.amazonaws.com;
      proxy_cache            cache;
      proxy_cache_valid      200 24h;
      proxy_cache_valid      403 15m;
      proxy_cache_use_stale  error timeout updating http_500 http_502 http_503 http_504;
      proxy_cache_lock       on;
      proxy_cache_bypass     $http_cache_purge;
      add_header             Cache-Control max-age=31536000;
      add_header             X-Cache-Status $upstream_cache_status;
    }}
}}

server {{
    listen 80;
    server_name {NAME};

    if ($host = {NAME}) {{
        return 301 https://$host$request_uri;
    }}

    return 404;
}}
"""


NGINX_INDEX_TEMPLATE = """
<html>
<head>
    <title>{NAME}</title>
</head>
<body>
    <h1>{NAME}</h1>
</body>
</html>
"""


NGINX_SITES = [
    ("quuux.org", NGINX_HOSTED_SITE_CONFIG, True, {"LOCATIONS": ""}),
    ("snake.quuux.org", NGINX_HOSTED_SITE_CONFIG, True, {"LOCATIONS": ""}),
    ("p.ound.town", NGINX_HOSTED_SITE_CONFIG, True, {"LOCATIONS": NGINX_SYNAPSE_LOCATIONS}),
    ("frink.quuux.org", NGINX_HOSTED_SITE_CONFIG, True, {"LOCATIONS": NGINX_PROMETHEUS_METRICS_LOCATIONS}),
    ("homephone.quuux.org", NGINX_PROXY_PASS_SITE_CONFIG, False, {"TARGET": "https://100.116.90.114:8000"}),
    ("atomic.quuux.org", NGINX_PROXY_PASS_SITE_CONFIG, False, {"TARGET": "http://100.80.129.57"}),
    ("liminal.quuux.org", NGINX_S3_PROXY_SITE_CONFIG, False, {"BUCKET": "liminal.quuux.org"}),
    ("rogue.quuux.org", NGINX_S3_PROXY_SITE_CONFIG, False, {"BUCKET": "rogue.quuux.org"}),
    ("rogue-api.quuux.org", NGINX_PROXY_PASS_NOAUTH_CONFIG, False, {"TARGET": "http://100.106.82.43:6543"}),
]


@task
def configure_nginx():
    nginx_conf_src = os.path.join(CONFIGS_PATH, "nginx.conf")
    put(nginx_conf_src, "/etc/nginx/nginx.conf", use_sudo=True)
    sudo("mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled")

    # sudo("sh -c \"echo -n 'user:' > /etc/nginx/htpasswd\"")
    # sudo("sh -c \"openssl passwd -apr1 >> /etc/nginx/htpasswd\"")

    for site, config_template, needs_dir, params in NGINX_SITES:

        if needs_dir:
            sudo(f"mkdir -p /var/www/{site}")

            html = NGINX_INDEX_TEMPLATE.format(NAME=site)
            put(StringIO(html), f"/var/www/{site}/index.html", use_sudo=True)

        config = config_template.format(NAME=site, **params)
        put(StringIO(config), f"/etc/nginx/sites-available/{site}", use_sudo=True)
        sudo(f"ln -s -f /etc/nginx/sites-available/{site} /etc/nginx/sites-enabled/{site}")

    sudo("systemctl restart nginx")


@task
def install_inspircd():
    run("git clone https://aur.archlinux.org/inspircd.git")
    run("cd inspircd && makepkg -sic")


@task
def bootstrap():
    update_packages()
    install_packages()
    configure_nginx()
    request_certs()

    install_inspircd()
    # configure_postfix() TODO
