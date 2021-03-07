# mesh-authentication

## Introduction
This code is a secure provision of mesh network parameters.

![alt text](images/Diagram.png?style=centerme)

The Server side authenticates nodes validating certificates based on the Elliptic Curve Integrated Encryption Scheme [(ECIES)](https://github.com/tiiuae/cryptolib)


Initially, the client sends a request to join the mesh network.
This request is attached with node certificates.
Once the server validates the certificate, it encrypts the mesh parameters and sends them back to the requested node.
The client detects the OS that is running (Ubuntu or OpenWRT) and sets the specific configuration of the mesh network.

The Ubuntu configuration is based on [mesh_com.](https://github.com/tiiuae/mesh_com)

##Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.
Two different configurations must be run on the server and on the client

### On the Client Side
```bash
pip install -r requirements/client-requirements.txt
```

### On the Server-Side
```bash
pip install -r requirements/server-requirements.txt
```
## Usage

On both sides, download the ECIES code
```bash
apt install clang make -y
git clone https://github.com/tiiuae/cryptolib.git
make
```
Create the certificate and provide it to all clients and server

```bash
make cert
scp ecc_key.der <user>@<nodeIP>:<path>
```
On the same folder, download this code
```bash
git clone
```
1) Run the server

```bash
python3 src/server-mesh.py
```
2) On the client node
```bash
python3 src/client/client-mesh.py -c ecc_key.der -s http://<ServerIP>:5000
```
On the server-side open a web browser and type
```bash
http://127.0.0.1:5000
```
A web page with the authenticated and no-authenticated nodes should be displayed

![alt text](images/server-screenshot.png?style=centerme)

