# mesh-authentication

## Introduction
This code is a secure provision of mesh network parameters. 

![alt text](images/Diagram.png)

The Server side authenticates nodes validating certificates based on the Elliptic Curve Integrated Encryption Scheme [(ECIES)](https://github.com/tiiuae/cryptolib)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.
Two different configurations must be run on the server and on the client

### On the Client Side
```bash
pip install -r requirements/client-requirements.txt
```

### On the Server Side
```bash
pip install -r requirements/server-requirements.txt
```
## Usageserver-screenshot.png

On both sides, download the ECIES code
```bash
apt install clang make -y
git clone https://github.com/tiiuae/cryptolib.git
make 
```
Create the certificate and provide it on all clients and server

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
On the server side open a web browser and type
```bash 
http://127.0.0.1:5000
```
A web page with the authenticated and no-authenticated nodes should be displayed
![alt text](images/server-screenshot.png)

