#!/bin/bash

# Production server script with gunicorn

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Business Operations API in Production Mode${NC}"
echo -e "${YELLOW}Environment: Production${NC}"
echo ""

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo -e "${YELLOW}Gunicorn not found. Installing...${NC}"
    pip install gunicorn
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo -e "${YELLOW}Make sure environment variables are set properly.${NC}"
fi

# Run the production server with gunicorn + uvicorn workers
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5



