#!/bin/bash

################################################################################
# Carbon6 OiS - Part 0: Pre-Flight System Prerequisites
# Agent: PRAXIS (Operations Director)
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

print_banner() {
    clear
    echo -e "${MAGENTA}"
    cat << "EOF"
██████╗  █████╗ ██████╗ ████████╗    ██████╗ 
██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝    ██╔══██╗
██████╔╝███████║██████╔╝   ██║       ██████╔╝
██╔═══╝ ██╔══██║██╔══██╗   ██║       ██╔══██╗
██║     ██║  ██║██║  ██║   ██║       ██████╔╝
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═════╝ 
     PRE-FLIGHT: System Prerequisites
        PRAXIS - Operations Director
EOF
    echo -e "${NC}\n"
}

print_agent() {
    echo -e "${MAGENTA}👤 PRAXIS:${NC} $1"
}

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

################################################################################
# System Checks
################################################################################

check_system() {
    print_agent "Let me verify your system meets the requirements..."
    echo ""
    
    local all_good=true
    
    # macOS check
    if [[ "$OSTYPE" == "darwin"* ]]; then
        print_status "Operating System: macOS $(sw_vers -productVersion)"
    else
        print_warning "Non-macOS system ($OSTYPE) - may require adjustments"
    fi
    
    # CPU
    local cpu_cores=$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo "unknown")
    print_status "CPU Cores: $cpu_cores"
    
    # RAM
    local total_mem=$(sysctl -n hw.memsize 2>/dev/null || echo "0")
    local total_mem_gb=$((total_mem / 1024 / 1024 / 1024))
    if [ $total_mem_gb -ge 8 ]; then
        print_status "RAM: ${total_mem_gb}GB"
    else
        print_warning "RAM: ${total_mem_gb}GB (8GB recommended)"
    fi
    
    # Disk space
    local available_space=$(df -h / | awk 'NR==2 {print $4}')
    print_status "Available Disk Space: $available_space"
    
    # Internet
    if ping -c 1 google.com &> /dev/null; then
        print_status "Internet Connection: Active"
    else
        print_error "Internet Connection: Failed"
        all_good=false
    fi
    
    echo ""
    
    if [ "$all_good" = false ]; then
        echo -e "${RED}System requirements not met. Please fix issues above.${NC}"
        exit 1
    fi
    
    print_status "System requirements met!"
    echo ""
}

################################################################################
# Homebrew Installation
################################################################################

install_homebrew() {
    print_agent "Checking for Homebrew package manager..."
    echo ""
    
    if command -v brew &> /dev/null; then
        print_status "Homebrew already installed: $(brew --version | head -n1)"
        brew update
    else
        print_agent "Installing Homebrew... (this may take a few minutes)"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add to PATH
        if [[ $(uname -m) == 'arm64' ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        else
            echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/usr/local/bin/brew shellenv)"
        fi
        
        print_status "Homebrew installed successfully"
    fi
    
    echo ""
}

################################################################################
# Development Tools
################################################################################

install_dev_tools() {
    print_agent "Installing development tools..."
    echo ""
    
    local tools=("git" "wget" "curl" "jq" "tree")
    
    for tool in "${tools[@]}"; do
        if command -v $tool &> /dev/null; then
            print_status "$tool already installed"
        else
            echo "Installing $tool..."
            brew install $tool
            print_status "$tool installed"
        fi
    done
    
    echo ""
}

################################################################################
# Language Runtimes
################################################################################

install_runtimes() {
    print_agent "Installing language runtimes..."
    echo ""
    
    # Node.js
    if command -v node &> /dev/null; then
        print_status "Node.js already installed: $(node --version)"
    else
        echo "Installing Node.js 20 LTS..."
        brew install node@20
        brew link node@20
        print_status "Node.js installed: $(node --version)"
    fi
    
    # Python
    if command -v python3 &> /dev/null; then
        print_status "Python already installed: $(python3 --version)"
    else
        echo "Installing Python 3.12..."
        brew install python@3.12
        print_status "Python installed: $(python3 --version)"
    fi
    
    echo ""
}

################################################################################
# Databases
################################################################################

install_databases() {
    print_agent "Installing database systems..."
    echo ""
    
    # PostgreSQL
    if command -v psql &> /dev/null; then
        print_status "PostgreSQL already installed"
    else
        echo "Installing PostgreSQL 15..."
        brew install postgresql@15
        brew services start postgresql@15
        sleep 3
        createdb $(whoami) 2>/dev/null || true
        print_status "PostgreSQL installed and started"
    fi
    
    # Redis
    if command -v redis-cli &> /dev/null; then
        print_status "Redis already installed"
    else
        echo "Installing Redis..."
        brew install redis
        brew services start redis
        print_status "Redis installed and started"
    fi
    
    echo ""
}

################################################################################
# Global NPM Packages
################################################################################

install_npm_packages() {
    print_agent "Installing global NPM packages..."
    echo ""
    
    local packages=("pm2" "pnpm" "typescript" "prisma" "nodemon")
    
    for package in "${packages[@]}"; do
        if npm list -g $package &> /dev/null; then
            print_status "$package already installed"
        else
            echo "Installing $package..."
            npm install -g $package
            print_status "$package installed"
        fi
    done
    
    echo ""
}

################################################################################
# SSH Keys
################################################################################

generate_ssh_keys() {
    print_agent "Checking SSH keys..."
    echo ""
    
    if [ -f ~/.ssh/id_ed25519 ]; then
        print_status "SSH key already exists"
    else
        echo "Generating SSH key..."
        ssh-keygen -t ed25519 -C "carbon6@$(hostname)" -f ~/.ssh/id_ed25519 -N ""
        eval "$(ssh-agent -s)"
        ssh-add ~/.ssh/id_ed25519
        print_status "SSH key generated"
        
        echo ""
        echo -e "${YELLOW}Your public SSH key:${NC}"
        cat ~/.ssh/id_ed25519.pub
        echo ""
    fi
    
    echo ""
}

################################################################################
# Verification
################################################################################

verify_installation() {
    print_agent "Verifying all installations..."
    echo ""
    
    local all_ok=true
    
    command -v brew &> /dev/null && print_status "Homebrew" || { print_error "Homebrew"; all_ok=false; }
    command -v git &> /dev/null && print_status "Git" || { print_error "Git"; all_ok=false; }
    command -v node &> /dev/null && print_status "Node.js" || { print_error "Node.js"; all_ok=false; }
    command -v npm &> /dev/null && print_status "npm" || { print_error "npm"; all_ok=false; }
    command -v python3 &> /dev/null && print_status "Python" || { print_error "Python"; all_ok=false; }
    command -v psql &> /dev/null && print_status "PostgreSQL" || { print_error "PostgreSQL"; all_ok=false; }
    command -v redis-cli &> /dev/null && print_status "Redis" || { print_error "Redis"; all_ok=false; }
    command -v pm2 &> /dev/null && print_status "PM2" || { print_error "PM2"; all_ok=false; }
    
    echo ""
    
    if [ "$all_ok" = true ]; then
        print_status "All prerequisites verified!"
        echo ""
        echo -e "${GREEN}Part 0 Complete!${NC}"
        echo "Ready for Part 1: Pre-Installation"
    else
        echo -e "${RED}Some installations failed. Please check errors above.${NC}"
        exit 1
    fi
    
    echo ""
}

################################################################################
# Main
################################################################################

main() {
    print_banner
    
    print_agent "Welcome! I'm PRAXIS, the Operations Director."
    print_agent "I'll prepare your system with all necessary prerequisites."
    echo ""
    
    read -p "Ready to begin? [Y/n]: " confirm
    [[ $confirm =~ ^[Nn]$ ]] && exit 0
    
    echo ""
    
    check_system
    install_homebrew
    install_dev_tools
    install_runtimes
    install_databases
    install_npm_packages
    generate_ssh_keys
    verify_installation
    
    echo "Duration: 10-15 minutes"
    echo ""
    read -p "Press Enter to continue..."
}

main
