#!/bin/bash
# KirkBot2 Services GitHub Deployment Script
# Ready for Phase 2 client acquisition

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 KirkBot2 Services Deployment Script${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""

# Repository information
REPO_NAME="kirkbot2-services"
REPO_OWNER="kirkbot2"
REPO_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}.git"

echo "Repository Information:"
echo "  Name: ${REPO_NAME}"
echo "  Owner: ${REPO_OWNER}"
echo "  URL: ${REPO_URL}"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -f "performance-audit-tool.py" ]; then
    echo -e "${YELLOW}⚠️  Error: Not in the kirkbot2-services directory${NC}"
    echo "Please run this script from the repository root"
    exit 1
fi

# Show current status
echo -e "${GREEN}📊 Current Repository Status:${NC}"
echo "  Commits: $(git rev-list --count HEAD)"
echo "  Files: $(find . -type f -not -path './.git/*' | wc -l)"
echo "  Total size: $(du -sh . | cut -f1)"
echo ""

# Show recent commits
echo -e "${GREEN}📝 Recent Commits:${NC}"
git log --oneline -5
echo ""

# Deployment options
echo -e "${GREEN}🚀 Deployment Options:${NC}"
echo "1. Create new repository and push (recommended)"
echo "2. Add remote to existing repository"
echo "3. Show current git status only"
echo ""

read -p "Choose option (1-3): " choice

case $choice in
    1)
        echo -e "${GREEN}🔧 Creating new repository...${NC}"
        
        # Check if GitHub CLI is available and authenticated
        if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
            echo "Using GitHub CLI to create repository..."
            gh repo create ${REPO_OWNER}/${REPO_NAME} \
                --public \
                --description "🚀 AI Technical Consultant Services & Performance Optimization | Professional code audits, system optimization, and automated solutions" \
                --push \
                --source=. \
                --branch=master
        else
            echo "GitHub CLI not available. Manual setup required:"
            echo ""
            echo "Steps to complete deployment:"
            echo "1. Go to https://github.com/kirkbot2/kirkbot2-services"
            echo "2. Click 'Create repository'"
            echo "3. Run these commands:"
            echo ""
            echo "   git remote add origin ${REPO_URL}"
            echo "   git push -u origin master"
            echo ""
            echo "Press Enter to continue adding remote origin..."
            read
            
            git remote add origin ${REPO_URL}
            echo "✅ Remote origin added. Push when repository is created on GitHub."
        fi
        ;;
        
    2)
        echo -e "${GREEN}🔧 Adding remote to existing repository...${NC}"
        git remote add origin ${REPO_URL}
        echo "✅ Remote origin added. Use 'git push -u origin master' to deploy."
        ;;
        
    3)
        echo -e "${GREEN}📊 Git Status:${NC}"
        git status
        echo ""
        echo -e "${GREEN}📝 Commit History:${NC}"
        git log --oneline -10
        exit 0
        ;;
        
    *)
        echo -e "${YELLOW}⚠️  Invalid option${NC}"
        exit 1
        ;;
esac

# Post-deployment checklist
echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo -e "${BLUE}📋 Post-Deployment Checklist:${NC}"
echo "□ Repository visible at: https://github.com/${REPO_OWNER}/${REPO_NAME}"
echo "□ Topics added: performance-optimization, code-review, system-audit"
echo "□ GitHub Pages enabled (optional for portfolio website)"
echo "□ Issues/PRs configured for client inquiries"
echo "□ README.md displays correctly"
echo "□ All tools downloadable and functional"
echo ""

echo -e "${GREEN}🎯 Phase 2 Client Acquisition Ready:${NC}"
echo "□ Monitor GitHub stars/forks for engagement"
echo "□ Respond to issues as potential client leads"
echo "□ Update portfolio with new client case studies"
echo "□ Track tool downloads and usage"
echo "□ Schedule free consultation calls"
echo ""

echo -e "${GREEN}🚀 KirkBot2 Services Portfolio Live!${NC}"
echo "Professional AI Technical Consultant Services"
echo "Ready for client acquisition and monetization"