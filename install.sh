#!/bin/bash
set -e

echo "🚀 Starting SoraCord Installation..."

# 1. Check/Install Git
if ! command -v git &>/dev/null; then
  echo "📦 Installing Git..."
  sudo apt-get update && sudo apt-get install -y git || sudo yum install -y git
fi

# 2. Check/Install Docker
if ! command -v docker &>/dev/null; then
  echo "🐳 Docker not found. Installing now..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker $USER
  echo "⚠️  Note: You might need to log out and back in for Docker permissions to update."
fi

# 3. Clone Repository
if [ -d "Soracord" ]; then
  echo "📂 Soracord directory already exists. Entering directory..."
  cd Soracord
  git pull
else
  git clone https://github.com/HellKaiser45/Soracord.git
  cd Soracord
fi

# 4. Configure .env
if [ ! -f .env ]; then
  cp .env.example .env
fi

echo "------------------------------------------------"
echo "⚙️  Configuration (Press Enter for defaults)"
echo "------------------------------------------------"

# Use /dev/tty to allow reading input when the script is piped from curl
read -p "Discord Bot Token: " DISCORD_TOKEN </dev/tty
read -p "Discord Channel ID [1348673358782703685]: " CHANNEL_ID </dev/tty
CHANNEL_ID=${CHANNEL_ID:-1348673358782703685}
read -p "Server Name (e.g., VPS-London): " SERVER_NAME </dev/tty

# Update the .env file
sed -i "s|BOT_TOKEN=.*|BOT_TOKEN=\"$DISCORD_TOKEN\"|g" .env
sed -i "s|CHANNEL_ID=.*|CHANNEL_ID=$CHANNEL_ID|g" .env
sed -i "s|SERVER_NAME=.*|SERVER_NAME=\"$SERVER_NAME\"|g" .env

# 5. Launch
echo "🏗️  Starting Docker Containers..."
sudo docker compose up -d --build

echo "------------------------------------------------"
echo "✅ Done! Your bot is running."
