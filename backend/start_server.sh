#!/bin/bash
# Start BioBoard Flask API Server

echo "Starting BioBoard API Server..."
echo "================================"
echo ""

# Check if we're in the backend directory
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3."
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Warning: Flask not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the server
echo "Starting server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
python3 app.py

