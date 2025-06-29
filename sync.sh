#!/usr/bin/env bash

for host in frink apu;
do
  echo "Syncing ${host}"
  rsync -raz --progress --ignore-errors ${host}/* ${host}:/home/marc/Docker/
  echo
done
