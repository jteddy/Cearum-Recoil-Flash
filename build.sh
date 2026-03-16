#!/bin/bash

echo "Installing system dependencies..."
sudo apt install -y python3-pip python3-tk python3-pil.imagetk

echo "Installing Python packages..."
pip3 install customtkinter pillow makcu pyserial --break-system-packages

echo "Adding .local/bin to PATH..."
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

echo "Creating py symlink..."
sudo apt remove pythonpy -y 2>/dev/null
sudo ln -sf /usr/bin/python3 /usr/local/bin/py

echo "Adding user to dialout group for MAKCU serial port access..."
sudo usermod -a -G dialout $USER

echo ""
echo "======================================================"
echo "IMPORTANT: You must log out and back in for the"
echo "dialout group to take effect, otherwise the MAKCU"
echo "device will show a permission denied error."
echo "======================================================"
echo ""
echo "Done! Once logged back in, run Cearum with:"
echo "  cd ~/Downloads/Cearum-Recoil-Flash && py main.pyw"
