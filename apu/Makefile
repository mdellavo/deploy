HOST := apu
SSH  := ssh $(HOST)
SCP  := scp

PACKAGES := \
	man-db logrotate vim sudo bash-completion \
	tmux ntp wget curl git jq \
	docker docker-compose \
	openssl htop bpytop tree strace dnsutils

.PHONY: all packages docker services clean

all: packages docker services

# ── packages ─────────────────────────────────────────────────────────────────

packages:
	$(SSH) "sudo pacman -Syu --noconfirm"
	$(SSH) "sudo pacman -S --needed --noconfirm $(PACKAGES)"

# ── docker ──────────────────────────────────────────────────────────────────

docker: docker-compose.yaml
	$(SSH) "sudo systemctl enable --now docker"
	$(SCP) docker-compose.yaml $(HOST):~/docker-compose.yaml
	$(SSH) "sudo docker compose -f ~/docker-compose.yaml up -d"

# ── services ────────────────────────────────────────────────────────────────

services: ntp

ntp:
	$(SSH) "sudo systemctl enable --now ntpd"

# ── util ─────────────────────────────────────────────────────────────────────

status:
	$(SSH) "systemctl status docker ntpd"

clean:
	$(SSH) "sudo docker compose -f ~/docker-compose.yaml down"
