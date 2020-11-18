import os
import requests
import json
import subprocess
import time

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import argparse

# Construct the argument parser
ap = argparse.ArgumentParser()

# Add the arguments to the parser
ap.add_argument("-prk", "--privkey", required=True, help="Private key file")
ap.add_argument("-pbk", "--pubkey", required=True, help="Private key file")
ap.add_argument("-s", "--server", required=True, help="Server IP:Port Address. Ex: 'http://192.168.15.14:5000'")

args = ap.parse_args()

# URL = 'https://192.168.15.14:5000' #
URL = args.server
print(URL)


def get_secret_message(key):
    response = requests.post(URL + '/api/add_message/1234',
                             files={'key': open(key, 'rb')})

    print('Encrypted Message: ' + str(response.content))

    return response.content


def get_key(key_file, passphrase=None):
    keys_cache = RSA.import_key(open(key_file).read(), passphrase)
    return keys_cache


def decrypt_full(data, private_key, passphrase=None, out_encoding='utf-8'):
    pksize = private_key.size_in_bytes()
    enc_session_key = data[:pksize]
    nonce = data[pksize:pksize + 16]
    tag = data[pksize + 16:pksize + 32]
    has_been_encoded = data[pksize + 32:pksize + 33]
    ciphertext = data[pksize + 33:]

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    output = cipher_aes.decrypt_and_verify(ciphertext, tag)

    # decode output if it was encoded at encryption time
    if out_encoding and has_been_encoded == b'Y':
        output = output.decode(out_encoding)

    print('Unencrypted Message: ' + output)

    return output


def create_config(response):
    res = json.loads(response)
    if res['gateway'] == True:
        config_file = open('/etc/config/lime-node', 'a+')
    else:
        nodeId = int(res['addr'].split('.')[-1]) - 1  # the IP is sequential, then it gaves me the nodeId.
        config_file = open('/etc/config/lime-node', 'w')
        config_file.write('config lime ' + "'system'" + '\n')
        config_file.write('\t' + 'option hostname ' + "'" + 'node' + str(nodeId) + "'" + '\n')
        config_file.write('\t' + 'option firstbootwizard_configured ' + "'" + 'true' + "'" + '\n\n')

    config_file.write('config wifi radio1' + '\n')
    config_file.write('\t' + 'list modes ' + "'ieee80211s'" + '\n')
    config_file.write('\t' + 'option ieee80211s_mesh_fwding ' + "'" + res['ieee80211s_mesh_fwding'] + "'" + '\n')
    config_file.write('\t' + 'option ieee80211s_mesh_id ' + "'" + res['ieee80211s_mesh_id'] + "'" + '\n')
    config_file.write('\t' + 'option channel ' + "'" + str(res['channel']) + "'" + '\n\n')

    config_file.write('config lime ' + "'network'" + '\n')
    config_file.write('\t' + 'list protocols ' + "'ieee80211s'" + '\n')
    config_file.write('\t' + 'list protocols ' + "'lan'" + '\n')
    config_file.write('\t' + 'list protocols ' + "'anygw'" + '\n')
    config_file.write('\t' + 'list protocols ' + "'" + 'batadv:' + res['batadv'] + "'" + '\n')
    config_file.write('\t' + 'list protocols ' + "'" + 'babeld:' + res['babeld'] + "'" '\n')
    config_file.write('\t' + 'list protocols ' + "'" + 'bmx7:' + res['bmx7'] + "'" + '\n')
    config_file.write('\t' + 'option main_ipv4_address ' + "'" + res['addr'] + '/16' + "'")

    config_file.close()


def final_settings():
    subprocess.call('lime-config', shell=True)
    time.sleep(2)
    subprocess.call('reboot', shell=True)


if __name__ == "__main__":
    key = get_key(args.privkey, 'test')
    res = decrypt_full(get_secret_message(args.pubkey), key, 'test')
    create_config(res)
    final_settings()
