#!/bin/bash

# Setup script for Business Operations Backend API
# This script sets up the development environment from scratch

set -e  # Exit on error

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Business Operations API - Environment Setup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

# Step 1: Check for uv
echo -e "${YELLOW}[1/6] Checking for uv package manager...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is not installed${NC}"
    echo -e "${YELLOW}Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Source the shell config to get uv in PATH
    if [ -f "$HOME/.zshrc" ]; then
        source "$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        source "$HOME/.bashrc"
    fi
    
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}Failed to install uv. Please install manually:${NC}"
        echo -e "${YELLOW}curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ uv is installed${NC}"
echo ""

# Step 2: Clean up stale environment
echo -e "${YELLOW}[2/6] Cleaning stale environment variables...${NC}"
unset VIRTUAL_ENV
unset PYTHONPATH
echo -e "${GREEN}✓ Environment cleaned${NC}"
echo ""

# Step 3: Create/verify virtual environment
echo -e "${YELLOW}[3/6] Setting up virtual environment...${NC}"
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Removing existing .venv...${NC}"
    rm -rf .venv
fi

uv venv
echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

# Step 4: Install dependencies
echo -e "${YELLOW}[4/6] Installing dependencies with uv...${NC}"
source .venv/bin/activate
uv pip install -r requirements.txt
echo -e "${GREEN}✓ Production dependencies installed${NC}"

if [ -f "requirements-dev.txt" ]; then
    uv pip install -r requirements-dev.txt
    echo -e "${GREEN}✓ Development dependencies installed${NC}"
fi
echo ""

# Step 5: Setup environment configuration
echo -e "${YELLOW}[5/6] Setting up environment configuration...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env from .env.example${NC}"
    else
        echo -e "${RED}Warning: .env.example not found${NC}"
    fi
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi
echo ""

# Step 6: Check PostgreSQL connection
echo -e "${YELLOW}[6/6] Checking database connection...${NC}"
if command -v pg_isready &> /dev/null; then
    if pg_isready -h localhost -p 5432 &> /dev/null; then
        echo -e "${GREEN}✓ PostgreSQL is running and accessible${NC}"
    else
        echo -e "${YELLOW}⚠ PostgreSQL is not running${NC}"
        echo -e "${YELLOW}  Start PostgreSQL or use Docker Compose:${NC}"
        echo -e "${YELLOW}  docker-compose up -d db${NC}"
    fi
else
    echo -e "${YELLOW}⚠ pg_isready not found (PostgreSQL client not installed)${NC}"
    echo -e "${YELLOW}  Make sure PostgreSQL is running or use Docker Compose:${NC}"
    echo -e "${YELLOW}  docker-compose up -d db${NC}"
fi
echo ""

# Success message
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Setup Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Start PostgreSQL (if not already running):"
echo -e "     ${YELLOW}docker-compose up -d db${NC}"
echo ""
echo -e "  2. Review and customize your .env file:"
echo -e "     ${YELLOW}vim .env${NC}"
echo ""
echo -e "  3. Run the development server:"
echo -e "     ${YELLOW}./run_dev.sh${NC}"
echo ""
echo -e "  4. Access the API:"
echo -e "     API:     ${YELLOW}http://localhost:8000${NC}"
echo -e "     Swagger: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "     ReDoc:   ${YELLOW}http://localhost:8000/redoc${NC}"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""

