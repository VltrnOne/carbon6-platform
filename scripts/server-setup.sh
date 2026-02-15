#!/bin/bash
# Carbon6 Production Server Setup
# Run this on your deployment server to prepare for automated deployments

set -e

echo "🚀 Carbon6 Production Server Setup"
echo "===================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (or use sudo)"
    exit 1
fi

echo "📦 Installing dependencies..."

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose already installed"
fi

# Install Certbot for SSL
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    apt-get install -y certbot python3-certbot-nginx
else
    echo "✅ Certbot already installed"
fi

# Install Git
if ! command -v git &> /dev/null; then
    echo "Installing Git..."
    apt-get install -y git
else
    echo "✅ Git already installed"
fi

echo ""
echo "👤 Creating deployment user..."

# Create deployment user
if ! id -u carbon6deploy &> /dev/null; then
    useradd -m -s /bin/bash carbon6deploy
    usermod -aG docker carbon6deploy
    echo "✅ User 'carbon6deploy' created"
else
    echo "✅ User 'carbon6deploy' already exists"
fi

echo ""
echo "📁 Setting up deployment directory..."

# Create deployment directory
mkdir -p /opt/carbon6
chown carbon6deploy:carbon6deploy /opt/carbon6

echo ""
echo "🔧 Configuring firewall..."

# Configure UFW firewall
ufw --force enable
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw status

echo ""
echo "🔐 SSH Configuration..."
echo ""
echo "⚠️  IMPORTANT: Add your public SSH key to allow deployments"
echo ""
echo "Run this on your LOCAL machine:"
echo "  cat ~/.ssh/id_rsa.pub"
echo ""
echo "Then run this on the SERVER:"
echo "  sudo -u carbon6deploy mkdir -p /home/carbon6deploy/.ssh"
echo "  sudo -u carbon6deploy nano /home/carbon6deploy/.ssh/authorized_keys"
echo "  # Paste your public key, save, and exit"
echo "  sudo chmod 700 /home/carbon6deploy/.ssh"
echo "  sudo chmod 600 /home/carbon6deploy/.ssh/authorized_keys"
echo ""

read -p "Press Enter after adding SSH key..."

echo ""
echo "🧪 Testing Docker..."

# Test Docker
docker run --rm hello-world > /dev/null 2>&1 && echo "✅ Docker working" || echo "❌ Docker test failed"

echo ""
echo "📊 System Information:"
echo "  Docker version: $(docker --version)"
echo "  Docker Compose: $(docker-compose --version)"
echo "  Certbot: $(certbot --version)"
echo "  Deployment user: carbon6deploy"
echo "  Deployment directory: /opt/carbon6"
echo ""

echo "✅ Server setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Clone Carbon6 repository to /opt/carbon6"
echo "  2. Configure GitHub Actions secrets:"
echo "     - DEPLOY_HOST: $(hostname -I | awk '{print $1}')"
echo "     - DEPLOY_USER: carbon6deploy"
echo "     - DEPLOY_SSH_KEY: Your private SSH key"
echo "  3. Set up DNS for thecarbon6.agency pointing to this server"
echo "  4. Run SSL setup: certbot --nginx -d thecarbon6.agency -d www.thecarbon6.agency"
echo "  5. Push to main branch to trigger deployment"
echo ""
