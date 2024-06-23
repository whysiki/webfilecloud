#!/bin/bash

# Reset system proxy settings
gsettings set org.gnome.system.proxy mode 'none'

# Reset environment variables
unset http_proxy
unset https_proxy
unset ftp_proxy
unset socks_proxy
unset no_proxy

# Reset apt proxy settings
sudo sed -i '/^Acquire::http::Proxy/d' /etc/apt/apt.conf
sudo sed -i '/^Acquire::https::Proxy/d' /etc/apt/apt.conf
sudo sed -i '/^Acquire::ftp::Proxy/d' /etc/apt/apt.conf
sudo sed -i '/^Acquire::socks::Proxy/d' /etc/apt/apt.conf

# Reset environment variables for apt
sudo sed -i '/^export http_proxy=/d' /etc/environment
sudo sed -i '/^export https_proxy=/d' /etc/environment
sudo sed -i '/^export ftp_proxy=/d' /etc/environment
sudo sed -i '/^export socks_proxy=/d' /etc/environment
sudo sed -i '/^export no_proxy=/d' /etc/environment

# Reset system-wide proxy settings for Snap
sudo snap set system proxy.https=''
sudo snap set system proxy.http=''
sudo snap set system proxy.ftp=''

# Reset proxy settings for systemd
sudo systemctl daemon-reload

# Restart affected services (you may need to customize this based on your system)
sudo systemctl restart NetworkManager
sudo systemctl restart systemd-resolved

echo "Proxy settings have been reset successfully."
