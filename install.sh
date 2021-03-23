#!/bin/bash

function command_exists {
  # check if command(s) exists and fail otherwise
  for cmd in $1; do
    echo -n "> Checking $cmd installed... "
    if ! command -v $cmd &> /dev/null; then
      echo "FALSE"
      echo "WARN: Require dependency "$cmd" but it's not installed. Installing..."
      sudo apt install --no-install-recommends $cmd -y
    else
      echo "TRUE"
    fi
  done
}

function menu_from_array()
{
  select choice; do
  # Check the selected menu item number
  if [ 1 -le "$REPLY" ] && [ "$REPLY" -le $# ];
  then
  break;
  else
  echo "Wrong selection: Select any number from 1-$#"
  fi
  done
}

function create_wpa_supplicant_conf {
cat <<EOF > wpa_supplicant_client_AP.conf
network={
  ssid="$1"
  psk="$2"
}
EOF
}

function ap_connect {
  echo '> Connecting to Access Point...'
  read -p "- SSID: " ssid
  read -p "- Password: " password
  create_wpa_supplicant_conf $ssid $password
  echo '> Please choose from the list of available interfaces...'
  interfaces_arr=($(ip link | awk -F: '$0 !~ "lo|vir|doc|eth|^[^0-9]"{print $2}'))
  menu_from_array "${interfaces_arr[@]}"
  sudo wpa_supplicant -B -i $choice -c wpa_supplicant_client_AP.conf
  sudo dhclient -v $choice
}

#-----------------------------------------------------------------------------#
echo '> Allow ssh and turn on netmanager so we can connect to this node...'
sudo ufw allow ssh
sudo nmcli networking on
# # Connect to AP
read -p "> We need to be connect to the same network as the server... Connect to an Access Point? (Y/N): " confirm
if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
  ap_connect
fi
# Provision the node with required packages
echo "> Checking required packages..."
command_exists "git make python3-pip batctl ssh clang libssl-dev net-tools iperf3 avahi-daemon avahi-dnsconfd avahi-utils libnss-mdns bmon isc-dhcp-server"
# Clone this repo
echo "> Cloning..."
git clone https://github.com/martin-tii/mesh-authentication.git
