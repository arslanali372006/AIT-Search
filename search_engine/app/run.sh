#!/bin/bash

# AIT Search Engine - Unified Launcher Script
# Starts both backend and frontend servers

echo "============================================================"
echo "🚀 AIT Search Engine - Starting Servers"
echo "============================================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped!"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Start backend
echo "📡 Starting backend API server..."
echo "   Directory: $BACKEND_DIR"
echo "   URL: http://localhost:8000"
cd "$BACKEND_DIR"
python3 -m uvicorn server:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "   PID: $BACKEND_PID"

# Wait for backend to be ready
echo ""
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Start frontend
echo ""
echo "🌐 Starting frontend server..."
echo "   Directory: $FRONTEND_DIR"
echo "   URL: http://localhost:8080"
cd "$FRONTEND_DIR"
python3 -m http.server 8080 &
FRONTEND_PID=$!
echo "   PID: $FRONTEND_PID"

sleep 2

echo ""
echo "============================================================"
echo "✅ Both servers are running!"
echo "============================================================"
echo ""
echo "📍 Access Points:"
echo "   Frontend:  http://localhost:8080"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "💡 Press Ctrl+C to stop both servers"
echo "============================================================"

# Try to open browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    sleep 1
    open http://localhost:8080
fi

# Wait for processes
wait
