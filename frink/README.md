``` sh
cd /var/lib/synapse

sudo -u synapse python -m synapse.app.homeserver \
      --server-name p.ound.town \
      --config-path /etc/synapse/homeserver.yaml \
      --generate-config \
      --report-stats=yes
      
git clone https://github.com/matrix-org/matrix-appservice-irc.git
npm i
```
