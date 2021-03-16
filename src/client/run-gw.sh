# !/bin/as
batctl gw_mode server 500mbit/500mbit
#bmx7 -c tunOut -inet4
#bmx7 -c tunIn inet4 /n 0.0.0.0/0
cat <<EOF > /tmp/ap-client.conf
network={
    ssid="TII-MANDREONI"
    psk="ssrcpassword"
}
EOF
sudo wpa_supplicant -i wlan0 -B -c /tmp/ap-client.conf &
dhclient -v wlan0