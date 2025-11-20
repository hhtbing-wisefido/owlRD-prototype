#!/bin/bash

echo "===================================="
echo "  owlRD Prototype API Server"
echo "  Starting on 0.0.0.0:8000"
echo "===================================="
echo ""
echo "Checking Python version..."
python3 --version
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt
echo ""
echo "Starting server..."
echo "Server will be accessible at:"
echo "  - http://localhost:8000"
echo "  - http://127.0.0.1:8000"
echo "  - http://YOUR_IP:8000 (局域网)"
echo ""
echo "API Documentation:"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
