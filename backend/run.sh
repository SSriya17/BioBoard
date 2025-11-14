#!/bin/bash

# Simple script to run the backend server

echo "=========================================="
echo "BioBoard Backend Server"
echo "=========================================="
echo ""
echo "Starting server on http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""
echo "=========================================="
echo ""

cd "$(dirname "$0")"
python3 app.py

