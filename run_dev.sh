#!/bin/bash

# Development server script with hot reload

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Business Operations API in Development Mode${NC}"
echo -e "${YELLOW}Environment: Development${NC}"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is not installed${NC}"
    echo -e "${YELLOW}Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating with uv...${NC}"
    uv venv
    echo -e "${GREEN}Installing dependencies with uv...${NC}"
    uv pip install -r requirements.txt
    uv pip install -r requirements-dev.txt
else
    echo -e "${GREEN}Virtual environment found. Activating...${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found.${NC}"
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}Copying .env.example to .env${NC}"
        cp .env.example .env
    else
        echo -e "${RED}Error: .env.example not found. Please create environment configuration.${NC}"
        exit 1
    fi
fi

# Export PYTHONPATH to ensure app module is found
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

echo ""
echo -e "${GREEN}Starting uvicorn server...${NC}"
echo -e "${YELLOW}API will be available at: http://localhost:8000${NC}"
echo -e "${YELLOW}Swagger docs: http://localhost:8000/docs${NC}"
echo ""

# Run the development server with auto-reload
uvicorn app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level debug \
    --reload-dir app



