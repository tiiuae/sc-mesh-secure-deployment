from flask import Flask, request, jsonify, json
import rsa
import base64
import asymcrypt
from getmac import get_mac_address
import subprocess
import netifaces

app = Flask(__name__)

aux = {'batadv': '120', 'babeld': '17',
       'ieee80211s_mesh_id': 'LiMe',
       'bmx7': '18',
       'ieee80211s_mesh_fwding': '0',
       'channel': 5, 'gateway': False}

ADDRESSES = {'00:00:00:00:00:00': '10.20.15.1'}

IP_PREFIX = '10.20.15'


@app.route('/api/add_message/<uuid>', methods=['GET', 'POST'])
def add_message(uuid):
    ip_address = request.remote_addr
    print("Requester IP: " + ip_address)
    mac = get_mac_address(ip=ip_address)
    ip_mesh = verify_addr(mac)
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

    command = 'ip route add ' + IP_PREFIX + '.0/24' + 'via ' + ip_gateway + ' dev ' + inter[
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)