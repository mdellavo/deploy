fab file to deploy stuff

```sh
brew install openssl@1.1 rust
env LDFLAGS="-L$(brew --prefix openssl@1.1)/lib" CFLAGS="-I$(brew --prefix openssl@1.1)/include" pip install cryptography
```

# Collectd

```sh
git clone https://aur.archlinux.org/liboping.git && cd liboping && makepkg -sic
git clone https://aur.archlinux.org/collectd.git && cd collectd && makepkg -sic
```

# Loki 

``` sh
sudo usermod -G systemd-journal,log promtail
sudo chgrp -R log /var/log
sudo chmod -R g+r /var/log
```

