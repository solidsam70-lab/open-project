#!/bin/bash
set -e

echo "JARVIS - AI Operating System Setup"
echo "=================================="

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Python 3 required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker required"; exit 1; }

# Create Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv backend/venv
source backend/venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Set up environment file
if [ ! -f backend/.env ]; then
    echo "Creating .env from template..."
    cp backend/.env.example backend/.env
    echo "Please edit backend/.env with your configuration"
fi

# Create data directories
mkdir -p data/postgres data/qdrant data/redis

# Start infrastructure services
echo "Starting PostgreSQL, Qdrant, and Redis..."
docker-compose up -d postgres qdrant redis

# Wait for services
echo "Waiting for services..."
sleep 5

# Run database migrations
echo "Running database migrations..."
cd backend
alembic upgrade head || echo "Migrations may need manual setup"
cd ..

echo ""
echo "JARVIS setup complete!"
echo ""
echo "Start the API server:"
echo "  cd backend && source venv/bin/activate && uvicorn jarvis.api.main:app --reload --port 8000"
echo ""
echo "Or start full stack:"
echo "  docker-compose up -d"
echo ""
echo "API docs: http://localhost:8000/docs"
