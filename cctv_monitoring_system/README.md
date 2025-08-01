# CCTV PPE Monitoring System

A comprehensive web-based CCTV monitoring system with real-time PPE (Personal Protective Equipment) violation detection, emergency alerts, and automated reporting.

## 🚀 Features

### 🛡️ PPE Violation Detection
- **Real-time detection** of missing helmets and safety vests
- **Fall detection** with emergency response
- **Fire and smoke detection** for safety monitoring
- **Confidence scoring** for accurate detections

### 📊 Live Monitoring Dashboard
- **Real-time statistics** with live counters
- **Violation heatmaps** showing high-risk areas
- **Camera PTZ controls** for Hikvision IP cameras
- **Live video feed** with detection overlays

### 🚨 Emergency Alert System
- **Automatic notifications** via email and WhatsApp
- **Custom sound alerts** for different violation types
- **Emergency popup modals** for critical incidents
- **Fall detection** with medical team notifications

### 📈 Automated Reporting
- **Daily/Weekly/Monthly** compliance reports
- **PDF generation** with charts and statistics
- **Violation logs** with timestamps and evidence
- **Trend analysis** and recommendations

### 🎥 Camera Integration
- **Hikvision IP camera** support
- **PTZ controls** (Pan, Tilt, Zoom)
- **RTSP streaming** integration
- **Snapshot capture** for evidence

## 🏗️ System Architecture

```
CCTV Monitoring System
├── Backend (FastAPI)
│   ├── Detection Model (YOLOv8)
│   ├── Database Manager (SQLAlchemy)
│   ├── Camera Manager (Hikvision)
│   ├── Notification Manager
│   ├── Violation Logger
│   └── Report Generator
├── Frontend (HTML/CSS/JS)
│   ├── Real-time Dashboard
│   ├── WebSocket Connections
│   ├── Emergency Alerts
│   └── Camera Controls
└── Data Storage
    ├── Violation Logs
    ├── Screenshots
    ├── Reports
    └── Statistics
```

## 📋 Requirements

### System Requirements
- **Python 3.8+**
- **OpenCV 4.8+**
- **CUDA support** (optional, for GPU acceleration)
- **Network access** to Hikvision camera
- **Web browser** with WebSocket support

### Hardware Requirements
- **CPU**: Intel i5 or equivalent
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 100GB for logs and screenshots
- **Network**: Stable connection to camera

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd cctv_monitoring_system
```

### 2. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the backend directory:
```env
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
```

### 4. Download the PPE Detection Model
Place your YOLOv8 model file at:
```
backend/models/my_model.pt
```

### 5. Create Required Directories
```bash
mkdir -p data/screenshots
mkdir -p data/charts
mkdir -p logs
mkdir -p reports
mkdir -p frontend/assets/sounds
```

## 🚀 Quick Start

### 1. Start the Backend Server
```bash
cd backend
python main.py
```

The server will start on `http://10.4.9.50:8000`

### 2. Access the Web Interface
Open your browser and navigate to:
```
http://10.4.9.50:8000
```

### 3. Configure Camera Connection
1. Go to the camera controls section
2. Test the connection using the "Home" button
3. Verify the video feed is displaying

## 📖 Usage Guide

### Dashboard Overview
The main dashboard consists of three sections:

1. **Left Sidebar**: Live statistics and camera controls
2. **Center**: Live video feed with detection overlays
3. **Right Sidebar**: Recent alerts and report generation

### Camera Controls
- **Home**: Return camera to default position
- **Pan Left/Right**: Horizontal camera movement
- **Tilt Up/Down**: Vertical camera movement
- **Zoom In/Out**: Adjust camera zoom level
- **Stop**: Halt all camera movement

### Emergency Alerts
When critical violations are detected:
1. **Emergency modal** appears automatically
2. **Sound alerts** play based on violation type
3. **Email/WhatsApp notifications** are sent
4. **Alert is logged** in the system

### Report Generation
1. Click on any report button (Daily/Weekly/Monthly)
2. System generates PDF with charts and statistics
3. Report downloads automatically
4. Contains violation summaries and recommendations

## 🔧 Configuration

### Camera Settings
Edit the camera configuration in `backend/models/camera_manager.py`:
```python
self.camera_ip = "10.3.8.111"
self.username = "admin"
self.password = "WOWO@2000"
```

### Notification Settings
Configure emergency contacts in `backend/models/notification.py`:
```python
self.emergency_contacts = {
    "medical_team": ["+1234567890", "+1234567891"],
    "security_team": ["+1234567892", "+1234567893"],
    "management": ["+1234567894", "+1234567895"]
}
```

### Detection Sensitivity
Adjust confidence thresholds in `backend/models/detection_model.py`:
```python
if confidence > 0.5:  # Change this value
    detections.append({...})
```

## 📊 API Endpoints

### Real-time Detection
- `POST /api/detect` - Run detection on current frame
- `GET /api/statistics` - Get live statistics
- `GET /api/violations` - Get violation history

### Camera Control
- `GET /api/camera/status` - Get camera connection status
- `POST /api/camera/control` - Control PTZ camera

### Reports
- `GET /api/reports/generate` - Generate compliance reports
- `POST /api/notifications/test` - Test notification system

### WebSocket
- `WS /ws` - Real-time updates and alerts

## 🛡️ Security Features

### Access Control
- **Local network** access only
- **HTTPS support** for secure connections
- **Authentication** for admin functions

### Data Protection
- **Encrypted storage** for sensitive data
- **Secure logging** of violations
- **Privacy compliance** for video data

### Network Security
- **Firewall rules** for camera access
- **VPN support** for remote monitoring
- **Intrusion detection** for unauthorized access

## 🔍 Troubleshooting

### Common Issues

#### Camera Connection Failed
1. Check camera IP address and credentials
2. Verify network connectivity
3. Test RTSP stream manually
4. Check firewall settings

#### Detection Not Working
1. Verify model file exists at `models/my_model.pt`
2. Check GPU drivers if using CUDA
3. Monitor system resources
4. Review detection logs

#### WebSocket Connection Issues
1. Check browser compatibility
2. Verify server is running
3. Check network connectivity
4. Review browser console for errors

#### Notification Failures
1. Verify email credentials
2. Check Twilio account settings
3. Test network connectivity
4. Review notification logs

### Log Files
- **Application logs**: `backend/logs/app.log`
- **Violation logs**: `logs/violations_YYYY-MM-DD.json`
- **Error logs**: `backend/logs/error.log`

## 📈 Performance Optimization

### GPU Acceleration
```bash
# Install CUDA toolkit
sudo apt-get install nvidia-cuda-toolkit

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_violations_timestamp ON violations(timestamp);
CREATE INDEX idx_violations_type ON violations(violation_type);
```

### Memory Management
- **Regular cleanup** of old screenshots
- **Database maintenance** for optimal performance
- **Cache management** for detection results

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Code Style
- **Python**: PEP 8 compliance
- **JavaScript**: ESLint configuration
- **CSS**: Prettier formatting
- **Documentation**: Clear docstrings

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- **API Documentation**: Available at `/docs` when server is running
- **User Guide**: See this README
- **Troubleshooting**: Check the troubleshooting section

### Contact
- **Email**: support@company.com
- **Phone**: +1-234-567-8900
- **Emergency**: +1-234-567-8901

## 🔄 Updates

### Version History
- **v1.0.0**: Initial release with basic PPE detection
- **v1.1.0**: Added emergency alerts and notifications
- **v1.2.0**: Enhanced reporting and analytics
- **v1.3.0**: Improved camera controls and UI

### Upcoming Features
- **Mobile app** for remote monitoring
- **AI-powered** violation prediction
- **Integration** with safety management systems
- **Advanced analytics** and machine learning

---

**⚠️ Important**: This system is designed for safety monitoring. Always ensure proper safety protocols are in place and that this system complements, rather than replaces, human supervision.