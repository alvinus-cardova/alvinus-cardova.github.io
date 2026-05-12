# CCTV PPE Monitoring System - Deployment Guide

This guide provides step-by-step instructions for deploying the CCTV PPE Monitoring System in various environments.

## 🚀 Quick Deployment

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cctv_monitoring_system
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

1. **Run the startup script**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

2. **Or manually install dependencies**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

## 🔧 Configuration

### 1. Camera Configuration

Edit the camera settings in `backend/models/camera_manager.py`:

```python
self.camera_ip = "10.3.8.111"      # Your camera IP
self.username = "admin"             # Camera username
self.password = "WOWO@2000"        # Camera password
```

### 2. Environment Variables

Copy the example environment file and update it:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your actual values:

```env
# Camera Configuration
CAMERA_IP=10.3.8.111
CAMERA_USERNAME=admin
CAMERA_PASSWORD=WOWO@2000

# Email Configuration
EMAIL_USERNAME=your_email@company.com
EMAIL_PASSWORD=your_email_password

# WhatsApp Configuration (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number
```

### 3. Model File

Place your YOLOv8 PPE detection model at:
```
backend/models/my_model.pt
```

## 🌐 Network Configuration

### Local Network Setup

1. **Configure server IP**
   - Edit `backend/main.py` line 280:
   ```python
   host="10.4.9.50"  # Your server IP
   ```

2. **Firewall configuration**
   ```bash
   # Allow incoming connections on port 8000
   sudo ufw allow 8000
   ```

3. **Camera network access**
   - Ensure the server can reach the camera IP: 10.3.8.111
   - Test connectivity: `ping 10.3.8.111`

### Production Deployment

1. **Reverse proxy setup (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       location /ws {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

2. **SSL certificate (Let's Encrypt)**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

## 📊 Database Setup

### SQLite (Default)
- No additional setup required
- Database file: `backend/cctv_monitoring.db`

### PostgreSQL (Production)
1. **Install PostgreSQL**
   ```bash
   sudo apt-get install postgresql postgresql-contrib
   ```

2. **Create database**
   ```sql
   CREATE DATABASE cctv_db;
   CREATE USER cctv_user WITH PASSWORD 'cctv_password';
   GRANT ALL PRIVILEGES ON DATABASE cctv_db TO cctv_user;
   ```

3. **Update environment**
   ```env
   DATABASE_URL=postgresql://cctv_user:cctv_password@localhost/cctv_db
   ```

## 🔔 Notification Setup

### Email Notifications

1. **Gmail setup**
   - Enable 2-factor authentication
   - Generate app password
   - Update `.env` file with credentials

2. **Custom SMTP**
   ```env
   SMTP_SERVER=smtp.your-provider.com
   SMTP_PORT=587
   EMAIL_USERNAME=your_email@domain.com
   EMAIL_PASSWORD=your_password
   ```

### WhatsApp Notifications

1. **Twilio setup**
   - Create Twilio account
   - Get Account SID and Auth Token
   - Purchase WhatsApp-enabled phone number

2. **Configure emergency contacts**
   Edit `backend/models/notification.py`:
   ```python
   self.emergency_contacts = {
       "medical_team": ["+1234567890", "+1234567891"],
       "security_team": ["+1234567892", "+1234567893"],
       "management": ["+1234567894", "+1234567895"]
   }
   ```

## 🎥 Camera Integration

### Hikvision Camera Setup

1. **Network configuration**
   - Set camera IP: 10.3.8.111
   - Username: admin
   - Password: WOWO@2000

2. **RTSP stream URL**
   ```
   rtsp://admin:WOWO@2000@10.3.8.111:554/Streaming/Channels/101
   ```

3. **Test connection**
   ```bash
   # Test RTSP stream
   ffplay rtsp://admin:WOWO@2000@10.3.8.111:554/Streaming/Channels/101
   ```

### Other Camera Brands

For other camera brands, modify `backend/models/camera_manager.py`:

```python
# For generic IP cameras
self.rtsp_url = f"rtsp://{self.username}:{self.password}@{self.camera_ip}:554/stream1"
```

## 🔍 Monitoring and Logs

### Log Files
- **Application logs**: `logs/app.log`
- **Violation logs**: `logs/violations_YYYY-MM-DD.json`
- **Error logs**: `logs/error.log`

### Health Monitoring
```bash
# Check application health
curl http://localhost:8000/health

# Monitor logs
tail -f logs/app.log

# Check disk usage
du -sh data/ logs/ reports/
```

### Performance Monitoring
```bash
# Monitor CPU and memory
htop

# Monitor network
iftop

# Monitor disk I/O
iotop
```

## 🔒 Security Considerations

### Network Security
1. **Firewall rules**
   ```bash
   # Allow only local network access
   sudo ufw allow from 192.168.1.0/24 to any port 8000
   ```

2. **VPN access**
   - Set up VPN for remote access
   - Configure VPN client on monitoring stations

### Data Security
1. **Encrypt sensitive data**
   ```bash
   # Encrypt database
   sqlcipher cctv_monitoring.db
   ```

2. **Regular backups**
   ```bash
   # Backup script
   tar -czf backup_$(date +%Y%m%d).tar.gz data/ logs/ reports/
   ```

## 🚨 Troubleshooting

### Common Issues

#### Camera Connection Failed
```bash
# Test network connectivity
ping 10.3.8.111

# Test RTSP stream
ffprobe rtsp://admin:WOWO@2000@10.3.8.111:554/Streaming/Channels/101

# Check firewall
sudo ufw status
```

#### Detection Not Working
```bash
# Check model file
ls -la backend/models/my_model.pt

# Check GPU (if using CUDA)
nvidia-smi

# Check system resources
free -h
df -h
```

#### WebSocket Issues
```bash
# Check browser console for errors
# Test WebSocket connection
wscat -c ws://localhost:8000/ws
```

### Performance Issues

#### High CPU Usage
1. **Reduce detection frequency**
   ```python
   # In backend/main.py
   await asyncio.sleep(2)  # Increase from 1 to 2 seconds
   ```

2. **Use GPU acceleration**
   ```bash
   # Install CUDA toolkit
   sudo apt-get install nvidia-cuda-toolkit
   ```

#### Memory Issues
1. **Clean up old files**
   ```bash
   # Remove old screenshots (older than 30 days)
   find data/screenshots -name "*.jpg" -mtime +30 -delete
   ```

2. **Optimize database**
   ```sql
   VACUUM;
   ANALYZE;
   ```

## 📈 Scaling

### Horizontal Scaling
1. **Load balancer setup**
   ```nginx
   upstream cctv_backend {
       server 192.168.1.10:8000;
       server 192.168.1.11:8000;
       server 192.168.1.12:8000;
   }
   ```

2. **Database clustering**
   - Set up PostgreSQL cluster
   - Configure read replicas

### Vertical Scaling
1. **Increase server resources**
   - More CPU cores
   - More RAM
   - SSD storage

2. **GPU acceleration**
   - Install NVIDIA GPU
   - Configure CUDA
   - Use GPU-optimized models

## 🔄 Updates and Maintenance

### System Updates
```bash
# Update application
git pull origin main
docker-compose down
docker-compose up -d --build

# Update dependencies
pip install -r requirements.txt --upgrade
```

### Database Maintenance
```sql
-- Clean old violations (older than 90 days)
DELETE FROM violations WHERE timestamp < NOW() - INTERVAL '90 days';

-- Optimize database
VACUUM ANALYZE;
```

### Log Rotation
```bash
# Configure logrotate
sudo nano /etc/logrotate.d/cctv-monitoring

# Add configuration
/path/to/cctv_monitoring_system/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 cctv cctv
}
```

## 📞 Support

### Getting Help
1. **Check logs**: `tail -f logs/app.log`
2. **Test endpoints**: `curl http://localhost:8000/health`
3. **Review documentation**: README.md
4. **Contact support**: support@company.com

### Emergency Contacts
- **Technical Support**: +1-234-567-8900
- **Emergency Response**: +1-234-567-8901
- **System Administrator**: admin@company.com

---

**⚠️ Important**: Always test the system thoroughly in a staging environment before deploying to production. Ensure all safety protocols are in place and that the system complements, rather than replaces, human supervision.