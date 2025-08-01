#!/bin/bash

# CCTV PPE Monitoring System Startup Script
# This script starts the backend server and serves the frontend

echo "🚀 Starting CCTV PPE Monitoring System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if required directories exist
if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found. Please run this script from the project root."
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo "❌ Frontend directory not found. Please run this script from the project root."
    exit 1
fi

# Create required directories if they don't exist
echo "📁 Creating required directories..."
mkdir -p data/screenshots
mkdir -p data/charts
mkdir -p logs
mkdir -p reports
mkdir -p frontend/assets/sounds

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

# Check if model file exists
if [ ! -f "models/my_model.pt" ]; then
    echo "⚠️  Warning: Model file 'models/my_model.pt' not found."
    echo "   Please place your YOLOv8 model file in the models directory."
    echo "   The system will run without detection capabilities."
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating default .env file..."
    cat > .env << EOF
# Camera Configuration
CAMERA_IP=10.3.8.111
CAMERA_USERNAME=admin
CAMERA_PASSWORD=WOWO@2000

# Email Configuration
EMAIL_USERNAME=admin@company.com
EMAIL_PASSWORD=your_email_password

# WhatsApp Configuration (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number

# Database Configuration
DATABASE_URL=sqlite:///./cctv_monitoring.db
EOF
    echo "📝 Please edit the .env file with your actual credentials."
fi

# Start the server
echo "🌐 Starting the server..."
echo "📍 Server will be available at: http://10.4.9.50:8000"
echo "📚 API documentation: http://10.4.9.50:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python main.py