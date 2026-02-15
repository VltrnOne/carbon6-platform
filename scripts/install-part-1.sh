#!/bin/bash
# Part 1: Pre-Installation (SCOUT)
set -e
source "$(dirname "$0")/lib/common.sh" 2>/dev/null || true

print_banner() {
    clear
    echo -e "${GREEN}PART 1: PRE-INSTALLATION${NC}"
    echo -e "${GREEN}Agent: SCOUT (Discovery)${NC}\n"
}

main() {
    print_banner
    echo "👤 SCOUT: Let's configure your Carbon6 installation..."
    echo ""
    
    # Installation mode
    echo "Select installation mode:"
    echo "  1) Developer (SQLite, fast)"
    echo "  2) Production (PostgreSQL, PM2)"
    echo "  3) Docker (containerized)"
    read -p "Mode [1-3]: " mode
    
    # Create .env file
    cp .env.example .env 2>/dev/null || true
    
    case $mode in
        1) 
            sed -i '' 's|DATABASE_URL=.*|DATABASE_URL="file:./dev.db"|' .env
            echo "✓ Developer mode configured"
            ;;
        2)
            sed -i '' 's|DATABASE_URL=.*|DATABASE_URL="postgresql://localhost/carbon6"|' .env
            echo "✓ Production mode configured"
            ;;
        3)
            echo "✓ Docker mode selected"
            ;;
    esac
    
    # Generate secrets
    JWT_SECRET=$(openssl rand -base64 48)
    sed -i '' "s|JWT_SECRET=.*|JWT_SECRET=\"$JWT_SECRET\"|" .env
    
    echo ""
    echo -e "${GREEN}Part 1 Complete!${NC}"
    echo "Ready for Part 2: Main Installation"
    echo ""
}

main
