#!/bin/bash

# Development server script with hot reload

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Business Operations API in Development Mode${NC}"
echo -e "${YELLOW}Environment: Development${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
else
    source .venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Using .env.example as template.${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and configure it.${NC}"
fi

# Run the development server with auto-reload
uvicorn app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level debug \
    --reload-dir app



