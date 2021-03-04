from flask import Flask, request, jsonify, json, render_template
import rsa
import base64
import asymcrypt
from getmac import get_mac_address
import subprocess
import netifaces
import pandas as pd

app = Flask(__name__)

aux_openwrt = {'batadv': '120', 'babeld': '17',
       'ieee80211s_mesh_id': 'ssrc',
       'bmx7': '18',
       'ieee80211s_mesh_fwding': '0',
       'channel': 5, 'gateway': False}

aux_ubuntu = {
 "api_version": 1,                 #"interface version for future purposes"
 "ssid": "gold",                   #"0-32 octets, UTF-8, shlex.quote chars limiting"
 "key": "foobar",                  #"key for the network"
 "enc": "wep",                     #"encryption (wep, wpa2, wpa3, sae)"
 "ap_mac": "00:11:22:33:44:55",    #"bssid for mesh network"
 "country": "fi",                  #"Country code, sets tx power limits and supported channels"
 "frequency": "5220",              #"wifi channel frequency, depends on the country code and HW"
 #"ip": "192.168.1.1",              #"select unique IP address"
 "subnet": "255.255.255.0",        #"subnet mask"
 "tx_power": "30",                 #"select 30dBm, HW and regulations limiting it correct level. Can be used to set lower dBm levels for testing purposes (e.g. 5dBm)"
 "mode": "mesh"                    #"mesh=mesh network, ap=debug hotspot"
}

ADDRESSES = {'00:00:00:00:00:00': '10.20.15.1'}

IP_PREFIX = '10.20.15'


@app.route('/api/add_message/<uuid>', methods=['GET', 'POST'])
def add_message(uuid):
    ip_address = request.remote_addr
    print("Requester IP: " + ip_address)
    mac = get_mac_address(ip=ip_address)
    ip_mesh = verify_addr(mac)
    aux = aux_ubuntu if uuid == 'Ubuntu' else aux
    if ip_mesh == IP_PREFIX + '.2':  # First node, then gateway
        aux['gateway'] = True
        add_default_route(ip_address)  # we will need to add the default route to communicate
    else:
        aux['gateway'] = False
    key = request.files['key']
    publicKey = key.read()
    #    print(publicKey)

    with open('public_key.pem', 'wb') as f:
        f.write(publicKey)

    aux['addr'] = ip_mesh
    SECRET_MESSAGE = json.dumps(aux)

    print(SECRET_MESSAGE)
    encrypted = asymcrypt.encrypt_data(SECRET_MESSAGE, 'public_key.pem')
    print(encrypted)

    return encrypted


def add_default_route(ip_gateway):
    inter = netifaces.interfaces()

    command = 'ip route add ' + IP_PREFIX + '.0/24 ' + 'via ' + ip_gateway + ' dev ' + inter[
        -1]  # assuming only 2 interfaces are presented

    subprocess.call(command, shell=True)


def verify_addr(mac):
    last_ip = ADDRESSES[list(ADDRESSES.keys())[-1]]  # get last ip
    last_octect = int(last_ip.split('.')[-1])  # get last ip octect
    if mac not in ADDRESSES:
        ip_mesh = IP_PREFIX + '.' + str(last_octect + 1)
        ADDRESSES[mac] = ip_mesh
    else:
        ip_mesh = ADDRESSES[mac]
    print('Assigned IP_Mesh: ' + ip_mesh)
    print(ADDRESSES)
    return ip_mesh


def printing():
    return ADDRESSES

@app.route('/')
def debug():
    addresses=printing()
    table = pd.DataFrame.from_dict(addresses, orient='index', columns=['Mesh IP Address'])
    table['MAC Address'] = table.index
    table.reset_index(drop=True, inplace=True)
    bes = table.to_html(classes='table table-striped', header=True, index=False)
    return    '<h3>Authenticated Nodes</h3>' +bes


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)