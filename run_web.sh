#!/bin/bash

echo "🌐 Starting Sigil Web UI..."
echo ""
echo "Make sure the API server is running on port 5000"
echo "Run ./run_api.sh in another terminal"
echo ""

cd web-ui

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Update the web UI to use the API server
export NEXT_PUBLIC_API_URL=http://localhost:5000

npm run dev
