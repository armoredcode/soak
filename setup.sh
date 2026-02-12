#!/bin/bash

VERSION=$(grep 'VERSION =' soak.py | cut -d '"' -f 2)

echo "--- Installing SOAK v$VERSION ---"

# 1. Build the Docker Image
echo "[1/3] Building SOAK Engine (openSUSE Tumbleweed)..."
docker build -t soak-engine .

# 2. Prepare the Wrapper
echo "[2/3] Setting up CLI wrapper..."
chmod +x soak.py

# 3. Create a symlink in /usr/local/bin
echo "[3/3] Creating global 'soak' command (requires sudo)..."
sudo ln -sf "$(pwd)/soak.py" /usr/local/bin/soak

echo "---------------------------------------"
echo "INSTALLATION COMPLETE!"
echo "Usage: soak /path/to/source"
echo "Example: soak /home/thesp0nge/tmp/spacewalk-web"
