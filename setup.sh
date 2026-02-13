#!/bin/bash

# Exit on error
set -e

# Colors for a better UX
BLUE='\033[94m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
NC='\033[0m' # No Color

echo -e "${BLUE}--- SOAK: Initializing Project Setup ---${NC}"

# 1. Detect Container Runtime
echo -e "${YELLOW}[1/3] Detecting container runtime...${NC}"
RUNTIME=""
if command -v podman &>/dev/null; then
  RUNTIME="podman"
elif command -v docker &>/dev/null; then
  RUNTIME="docker"
else
  echo -e "${RED}[ERROR] Neither Podman nor Docker was found. Please install one to use SOAK.${NC}"
  exit 1
fi
echo -e "${GREEN}[*] Found $RUNTIME. Using it as the primary engine.${NC}"

# 2. Extract Version for branding
VERSION=$(grep 'VERSION =' soak.py | cut -d '"' -f 2 || echo "unknown")
echo -e "${GREEN}[*] Preparing SOAK v$VERSION...${NC}"

# 3. Build the Engine
echo -e "${YELLOW}[2/3] Building SOAK Engine (openSUSE Tumbleweed base)...${NC}"
echo -e "${BLUE}This might take a few minutes as we install SAST tools...${NC}"

# We use the detected runtime to build
$RUNTIME build -t soak-engine .

# 4. Global Command Setup
echo -e "${YELLOW}[3/3] Setting up global CLI command...${NC}"
chmod +x soak.py

# Create symlink in /usr/local/bin
# We use sudo because /usr/local/bin is usually restricted
echo -e "${BLUE}Requesting sudo to create symlink at /usr/local/bin/soak...${NC}"
if sudo ln -sf "$(pwd)/soak.py" /usr/local/bin/soak; then
  echo -e "${GREEN}[*] Symlink created successfully.${NC}"
else
  echo -e "${RED}[ERROR] Failed to create symlink. You can still run SOAK manually via ./soak.py${NC}"
fi

# Final Summary
echo -e "\n---------------------------------------"
echo -e "${GREEN}SOAK v$VERSION IS READY!${NC}"
echo -e "Runtime: $RUNTIME"
echo -e "Usage:   ${BLUE}soak /path/to/code${NC}"
echo -e "Example: ${BLUE}soak ~/projects/spacewalk-web -o ./reports${NC}"
echo -e "---------------------------------------"
