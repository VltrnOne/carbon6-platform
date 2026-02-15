#!/bin/bash
# Part 2: Main Installation (GENESIS)
set -e

print_banner() {
    clear
    echo -e "\033[0;36mPART 2: MAIN INSTALLATION\033[0m"
    echo -e "\033[0;36mAgent: GENESIS (Divine Orchestrator)\033[0m\n"
}

main() {
    print_banner
    echo "👤 GENESIS: Coordinating installation across all cores..."
    echo ""
    
    # Install dependencies
    echo "📦 Installing dependencies..."
    npm ci --prefer-offline
    echo "✓ Dependencies installed"
    
    # Generate Prisma
    echo ""
    echo "🔧 Generating Prisma client..."
    npx prisma generate
    echo "✓ Prisma client generated"
    
    # Database setup
    echo ""
    echo "💾 Setting up database..."
    npx prisma db push --skip-generate
    npx prisma db seed 2>/dev/null || echo "No seed data"
    echo "✓ Database ready"
    
    # Build application
    echo ""
    echo "🏗️  Building application..."
    npm run build
    echo "✓ Application built"
    
    # Start with PM2
    echo ""
    echo "🚀 Starting services..."
    pm2 start ecosystem.config.js 2>/dev/null || npm start &
    sleep 5
    echo "✓ Services started"
    
    # Verify
    echo ""
    echo "🏥 Health check..."
    curl -s http://localhost:3006/api/health > /dev/null && echo "✓ Platform online" || echo "⚠ Platform not responding"
    
    echo ""
    echo -e "\033[0;32mPart 2 Complete!\033[0m"
    echo "Ready for Part 3: Post-Installation"
    echo ""
}

main
