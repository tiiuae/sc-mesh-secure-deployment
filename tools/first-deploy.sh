#!/bin/bash

sudo ufw allow ssh
sudo nmcli networking on
sudo apt install -y git make python3-pip batctl ssh clang libssl-dev net-tools iperf3

git clone https://github.com/martin-tii/mesh-authentication.git
