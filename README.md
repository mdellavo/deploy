# deploy

Infrastructure and provisioning for quuux.org and related hosts.

## Overview

Two kinds of hosts:

- **ralph** — AWS EC2 instance (Ubuntu). Runs nginx, postfix, dovecot, inspircd, and docker containers (synapse, postgres, cadvisor, rogue). Managed via Terraform + cloud-init.
- **apu** — local Arch Linux machine. Runs docker containers. Managed via a Makefile over SSH.

AWS infrastructure (VPC, DNS, S3, RDS, IAM) is defined in `infra/` and applied with Terraform.

---

## Infra (Terraform)

All AWS resources live in `infra/main.tf`.

```sh
cd infra
terraform init       # first time only
terraform plan
terraform apply
```

Resources managed:
- VPC, subnets, routing, security groups
- EC2 instance (`ralph`), Elastic IP, IAM role
- RDS postgres instance
- Route53 zones and records for `quuux.org`, `marcdellavolpe.com`, `ound.town`, and others
- S3 buckets (`quuux-bootstrap`, `liminal.quuux.org`, `rogue.quuux.org`, logs)

---

## ralph (EC2, Ubuntu)

ralph is provisioned via cloud-init on first boot. The cloud-init config is assembled from separate files and published to S3, then referenced by the instance user data.

### Editing config

Config files live under `ralph/files/`:

```
ralph/
  base.yaml                   # packages, runcmd, debconf
  files/
    nginx/sites/              # per-site nginx configs
    postfix/                  # main.cf, virtual, aliases
    dovecot/                  # dovecot.conf
    inspircd/                 # inspircd.conf
    docker/                   # docker-compose.yaml
    scripts/setup-certs.sh    # run after DNS propagates
```

### Build and publish

After editing any file under `ralph/`:

```sh
cd ralph
python3 build.py
```

This assembles `ralph/cloud-init.yaml` and uploads it to `s3://quuux-bootstrap/ralph-cloud-init.yaml`.

Then run `terraform apply` from `infra/` to update the EC2 user data reference if needed (the S3 object update is picked up automatically on new instance launches).

### First boot

On launch, the instance fetches `ralph-cloud-init.yaml` from S3 and runs it. This installs all packages, writes config files, and starts services.

Nginx, postfix, and dovecot require TLS certificates. After the instance is up and DNS records are pointing at the Elastic IP, SSH in and run:

```sh
sudo /root/setup-certs.sh
```

### Subsequent deploys

cloud-init only runs on first boot. For config changes after launch, apply them manually over SSH or replace the instance.

---

## apu (local Arch Linux)

apu is provisioned via `apu/Makefile` over SSH. It assumes `apu` is configured in `~/.ssh/config`.

```sh
cd apu
make            # update packages, start docker, enable services
make packages   # pacman -Syu + install packages
make docker     # push docker-compose.yaml and bring containers up
make services   # enable ntp
make status     # check service status
```

Add `docker-compose.yaml` to `apu/` before running `make docker`.

Override the target host with `make HOST=192.168.1.x`.
