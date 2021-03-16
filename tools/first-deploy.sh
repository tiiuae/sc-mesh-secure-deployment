#!/bin/bash

sudo ufw allow ssh
sudo nmcli networking on
sudo apt install -y git make python3-pip batctl ssh clang libssl-dev net-tools
