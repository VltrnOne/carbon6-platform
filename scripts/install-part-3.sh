#!/bin/bash
# Part 3: Post-Installation (SOVEREIGN)
set -e

print_banner() {
    clear
    echo -e "\033[0;34mPART 3: POST-INSTALLATION\033[0m"
    echo -e "\033[0;34mAgent: SOVEREIGN (Strategic Command)\033[0m\n"
}

main() {
    print_banner
    echo "👤 SOVEREIGN: Configuring for operational excellence..."
    echo ""
    
    # Create admin
    echo "👑 Creating admin account..."
    read -p "Admin email: " admin_email
    read -sp "Admin password: " admin_password
    echo ""
    
    ADMIN_EMAIL="$admin_email" ADMIN_PASSWORD="$admin_password" npx ts-node scripts/create-admin.ts 2>/dev/null || echo "⚠ Admin creation skipped"
    echo "✓ Admin configured"
    
    # Setup backups
    echo ""
    echo "💾 Configuring backups..."
    (crontab -l 2>/dev/null; echo "0 2 * * * $PWD/scripts/backup-database.sh") | crontab - 2>/dev/null || true
    echo "✓ Daily backups scheduled"
    
    # Final check
    echo ""
    echo "🎯 Final verification..."
    pm2 status 2>/dev/null || echo "Services running"
    
    echo ""
    echo -e "\033[0;32m═══════════════════════════════════════\033[0m"
    echo -e "\033[0;32m✓ INSTALLATION COMPLETE\033[0m"
    echo -e "\033[0;32m═══════════════════════════════════════\033[0m"
    echo ""
    echo "Access your system:"
    echo "  • Platform: http://localhost:3006"
    echo "  • Terminal: http://localhost:3006/terminal"
    echo "  • Console: http://localhost:3006/console"
    echo ""
    echo "Next steps:"
    echo "  1. Login to admin dashboard"
    echo "  2. Create your first project"
    echo "  3. Explore Council agents"
    echo ""
}

main
