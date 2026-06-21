HOST := apu
SSH  := ssh $(HOST)
SCP  := scp

PACKAGES := \
	man-db logrotate vim sudo bash-completion \
	tmux ntp wget curl git jq \
	docker docker-compose \
	openssl htop bpytop tree strace dnsutils \
	cifs-utils

.PHONY: all packages docker services sync mounts clean

all: packages docker services sync mounts

# ── packages ─────────────────────────────────────────────────────────────────

packages:
	$(SSH) "sudo pacman -Syu --noconfirm"
	$(SSH) "sudo pacman -S --needed --noconfirm $(PACKAGES)"

# ── docker ──────────────────────────────────────────────────────────────────

DOCKER_DIR := ~/Docker

docker: docker-compose.yaml
	$(SSH) "sudo systemctl enable --now docker"
	$(SSH) "mkdir -p $(DOCKER_DIR)"
	$(SCP) docker-compose.yaml $(HOST):$(DOCKER_DIR)/docker-compose.yaml
	$(SSH) "sudo docker compose -f $(DOCKER_DIR)/docker-compose.yaml up -d"

# ── services ────────────────────────────────────────────────────────────────

services: ntp

ntp:
	$(SSH) "sudo systemctl enable --now ntpd"

# ── mounts ──────────────────────────────────────────────────────────────────

FSTAB_MEDIA := //synology.local/Media /media cifs _netdev,nofail,username=user,password=user,workgroup=WORKGROUP,file_mode=0777,dir_mode=0777,vers=2.0 0 0

DIRS := dashy syncthing plex sabnzbd unifi unifi-backup prometheus grafana blackbox-exporter radarr sonarr

sync:
	rsync -av $(DIRS) $(HOST):$(DOCKER_DIR)/

mounts:
	$(SSH) "sudo mkdir -p /media"
	$(SSH) "grep -qxF '$(FSTAB_MEDIA)' /etc/fstab || echo '$(FSTAB_MEDIA)' | sudo tee -a /etc/fstab"
	$(SSH) "sudo mount -a"

# ── util ─────────────────────────────────────────────────────────────────────

status:
	$(SSH) "systemctl status docker ntpd"

clean:
	$(SSH) "sudo docker compose -f $(DOCKER_DIR)/docker-compose.yaml down"
