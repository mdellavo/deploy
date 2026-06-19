#!/bin/bash
# Run after DNS is pointed at this instance and has propagated.
set -e

EMAIL="marc.dellavolpe@gmail.com"
CERTS=(
  "quuux.org"
  "liminal.quuux.org"
  "rogue.quuux.org"
  "rogue-api.quuux.org"
  "p.ound.town"
)

# Generate DH params for InspIRCd if not already present
if [ ! -f /etc/inspircd/dhparams.pem ]; then
  openssl dhparam -out /etc/inspircd/dhparams.pem 2048
fi

for domain in "${CERTS[@]}"; do
  certbot run --nginx -m "$EMAIL" --agree-tos -d "$domain"
done

systemctl restart postfix
systemctl restart dovecot
systemctl restart inspircd
systemctl restart nginx

echo "Done. Certs provisioned and services restarted."
