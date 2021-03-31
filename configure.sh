#!/bin/bash

function help {
echo " ./configure.sh"
echo "     -s               configure as server"
echo "     -c               configure as client"
echo "     --help           this help menu"
echo ""
exit 1
}

#-----------------------------------------------------------------------------#

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
cat <<EOF > tools/wpa_tools/wpa_supplicant_client_AP.conf
network={
  ssid="$1"
  psk="$2"
}
EOF
}


#-----------------------------------------------------------------------------#

function ap_connect {
  echo '> Connecting to Access Point...'
  read -p "- SSID: " ssid
  read -p "- Password: " password
  create_wpa_supplicant_conf $ssid $password
  echo '> Please choose from the list of available interfaces...'
  interfaces_arr=($(ip link | awk -F: '$0 !~ "lo|vir|doc|eth|^[^0-9]"{print $2}'))
  menu_from_array "${interfaces_arr[@]}"
  sudo wpa_supplicant -B -i $choice -c tools/wpa_tools/wpa_supplicant_client_AP.conf
  sudo dhclient -v $choice
}

function ap_create {
  echo '> Creating a Mesh Access Point...'
  echo '> Please choose from the list of available interfaces...'
  interfaces_arr=($(ip link | awk -F: '$0 !~ "lo|vir|doc|eth|^[^0-9]"{print $2}'))
  menu_from_array "${interfaces_arr[@]}"
  cd tools/wpa_tools
  chmod +x access_point_wpa_supplicant.sh
  sudo bash access_point_wpa_supplicant.sh $choice
  cd ../..
}

function access_point {
  echo '> Do you wish to...'
  hotspot_arr=('Connect to a hotspot?' 'Create a hotspot?')
  menu_from_array "${hotspot_arr[@]}"
  if [ $REPLY == "1" ]; then
    ap_connect
  elif [[ $REPLY == "2" ]]; then
    ap_create
  fi
}





function server {
  echo '> Configuring the server...'
  # Create a certificate
  make certificate
  # Make the server
  make server
  # Advertise the server using avahi (zeroconf)
  avahi-publish-service mesh_server _http._tcp 5000 &
  sudo python3 src/server-mesh.py -c src/ecc_key.der
}

function client {
  echo '> Configuring the client...'
  # Make the server
  make client
  # Connect to the same AP as the server
  read -p "> We need to be connect to the same network as the server... Connect to an Access Point? (Y/N): " confirm
  if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    ap_connect
  fi
  echo -n '> Server discovery...'
  # get server IPv4 and hostname
  while ! [ "$server_details" ] ; do
    server_details=$(timeout 7 avahi-browse -rptfl _http._tcp | awk -F';' '$1 == "=" && $3 == "IPv4" && $4 == "mesh_server" {print $8 " " $7}')
  done
  # split ip/host into separate vars
  server_details=($(sed -r 's/\b.local\b//g' <<< $server_details))
  server_ip=${server_details[0]}
  server_host=${server_details[1]}
  echo "> We will use src/ecc_key.der if it already exists, or we can try and fetch it..."
  read -p "> Do you want to fetch the certificate from the server $server_host@$server_ip? (Y/N): " confirm
  if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo '> Fetching certificate from server...'
    read -p "- Server Username: " server_user
    # pull the key from the server
    scp $server_user@$server_ip:/home/$server_user/mesh-authentication/src/ecc_key.der src/ecc_key.der
  fi

  echo '> Configuring the client and connecting to server...'
  sudo python3 src/client/client-mesh.py -c src/ecc_key.der -s http://$server_ip:5000
}



#-----------------------------------------------------------------------------#
echo '=== SSRC Mesh PoC Configuration ==='

PARAMS=""
while (( "$#" )); do
  case "$1" in
    -s)
      server
      shift
      ;;
    -c)
      client
      NOAP=1
      shift
      ;;
    -ap)
      access_point
      shift
      ;;
    --help)
      help
      shift 2
      ;;
    *) # preserve positional arguments
      PARAMS="$PARAMS $1"
      shift
      ;;
  esac
done
