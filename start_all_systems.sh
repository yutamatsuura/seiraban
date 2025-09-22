#!/bin/bash

# Sindankantei System Startup Script
# This script starts all required services for the fortune-telling system

echo "🔮 Starting Sindankantei Fortune-telling System..."

# Function to check if a port is already in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Function to start a service in the background
start_service() {
    local name=$1
    local command=$2
    local dir=$3

    echo "🚀 Starting $name..."
    cd "$dir"
    eval "$command" &
    echo "✅ $name started (PID: $!)"
}

# Check if we're in the right directory
if [[ ! -d "system" || ! -d "frontend" || ! -d "backend" ]]; then
    echo "❌ Please run this script from the inoue4 root directory"
    exit 1
fi

# Get the current directory
PROJECT_ROOT=$(pwd)

# Start Backend (Port 8502)
if check_port 8502; then
    start_service "Backend API" "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8502 --reload" "$PROJECT_ROOT"
else
    echo "⏭️  Backend already running on port 8502"
fi

# Start Frontend (Port 3003)
if check_port 3003; then
    start_service "Frontend (Vue.js)" "cd frontend && npm run dev" "$PROJECT_ROOT"
else
    echo "⏭️  Frontend already running on port 3003"
fi

# Start Kyusei System (Port 3001)
if check_port 3001; then
    start_service "Kyusei System" "cd system/kyuuseikigaku-kichihoui/src && python3 -m http.server 3001" "$PROJECT_ROOT"
else
    echo "⏭️  Kyusei system already running on port 3001"
fi

# Start Seimei System (Port 3002)
if check_port 3002; then
    start_service "Seimei System" "cd system/seimeihandan/src && python3 -m http.server 3002" "$PROJECT_ROOT"
else
    echo "⏭️  Seimei system already running on port 3002"
fi

echo ""
echo "🎉 All systems started successfully!"
echo ""
echo "📋 Service Status:"
echo "   • Frontend (Vue.js):     http://localhost:3003"
echo "   • Backend API:           http://localhost:8502"
echo "   • Kyusei System:         http://localhost:3001"
echo "   • Seimei System:         http://localhost:3002"
echo ""
echo "🔮 Open http://localhost:3003 in your browser to access the application"
echo ""
echo "⚠️  Note: Keep this terminal open to maintain all services"
echo "   Press Ctrl+C to stop all services"

# Keep the script running
wait