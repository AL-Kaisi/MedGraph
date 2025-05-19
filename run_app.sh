#!/bin/bash

echo "Starting MedGraph Application..."
cd /Users/mohamed.al-kaisi/Desktop/MedGraph

# Activate virtual environment
source venv/bin/activate

# Run the Flask app in the background
python app/flask_app.py &
APP_PID=$!

# Wait for the app to start
sleep 3

# Open the browser
echo "Opening browser at http://localhost:5001"
open http://localhost:5001

# Keep the script running
echo "Application is running. Press Ctrl+C to stop."
wait $APP_PID