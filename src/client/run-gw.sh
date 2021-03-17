#!/bin/bash

batctl gw_mode server 500mbit/500mbit
#bmx7 -c tunOut -inet4
#bmx7 -c tunIn inet4 /n 0.0.0.0/0
if [ ! -f /home/ap-client.conf ]; then
  cat <<EOF > /home/ap-client.conf
    network={
    ssid="TII-MANDREONI"
    psk="ssrcpassword"
  }
EOF
fi

sudo wpa_supplicant -i wlan0 -B -c /home/ap-client.conf &
dhclient -v wlan0