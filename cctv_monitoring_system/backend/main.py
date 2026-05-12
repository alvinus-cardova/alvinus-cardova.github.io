from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import asyncio
import json
import logging
from datetime import datetime, timedelta
import os
from pathlib import Path

from models.detection_model import PPEDetectionModel
from models.database import DatabaseManager
from models.notification import NotificationManager
from models.violation_logger import ViolationLogger
from models.report_generator import ReportGenerator
from models.camera_manager import CameraManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CCTV PPE Monitoring System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
notification_manager = NotificationManager()
violation_logger = ViolationLogger()
report_generator = ReportGenerator()
camera_manager = CameraManager()

# Load PPE detection model
try:
    detection_model = PPEDetectionModel("models/my_model.pt")
    logger.info("PPE Detection model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load PPE detection model: {e}")
    detection_model = None

# WebSocket connections for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                await self.disconnect(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize database and start background tasks"""
    await db_manager.initialize()
    asyncio.create_task(violation_monitoring_task())
    asyncio.create_task(daily_report_task())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await db_manager.close()

@app.get("/")
async def root():
    """Serve the main monitoring dashboard"""
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": detection_model is not None
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/detect")
async def detect_violations():
    """Real-time PPE violation detection endpoint"""
    if not detection_model:
        raise HTTPException(status_code=500, detail="Detection model not loaded")
    
    try:
        # Get frame from camera
        frame = await camera_manager.get_frame()
        if frame is None:
            raise HTTPException(status_code=500, detail="Failed to get camera frame")
        
        # Run detection
        results = detection_model.detect(frame)
        
        # Process violations
        violations = process_violations(results, frame)
        
        # Log violations
        for violation in violations:
            await violation_logger.log_violation(violation)
        
        # Send real-time updates
        await manager.broadcast(json.dumps({
            "type": "detection_update",
            "violations": violations,
            "timestamp": datetime.now().isoformat()
        }))
        
        return {
            "status": "success",
            "violations": violations,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/violations")
async def get_violations(
    start_date: str = None,
    end_date: str = None,
    violation_type: str = None,
    limit: int = 100
):
    """Get violation history with filters"""
    try:
        violations = await db_manager.get_violations(
            start_date=start_date,
            end_date=end_date,
            violation_type=violation_type,
            limit=limit
        )
        return {"violations": violations}
    except Exception as e:
        logger.error(f"Error fetching violations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/statistics")
async def get_statistics():
    """Get real-time statistics"""
    try:
        stats = await db_manager.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notifications/test")
async def test_notification():
    """Test notification system"""
    try:
        await notification_manager.send_emergency_alert("Test alert", "Test location")
        return {"status": "success", "message": "Test notification sent"}
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/generate")
async def generate_report(
    report_type: str = "daily",
    start_date: str = None,
    end_date: str = None
):
    """Generate compliance reports"""
    try:
        report_path = await report_generator.generate_report(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date
        )
        return FileResponse(report_path, media_type="application/pdf")
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/camera/status")
async def get_camera_status():
    """Get camera connection status"""
    try:
        status = await camera_manager.get_status()
        return status
    except Exception as e:
        logger.error(f"Error getting camera status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/camera/control")
async def control_camera(
    action: str,
    pan: float = 0,
    tilt: float = 0,
    zoom: float = 1
):
    """Control Hikvision PTZ camera"""
    try:
        result = await camera_manager.control_ptz(action, pan, tilt, zoom)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error controlling camera: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def process_violations(results, frame):
    """Process detection results and identify violations"""
    violations = []
    
    # Extract detections
    persons = []
    helmets = []
    vests = []
    falls = []
    fires = []
    smoke = []
    
    for detection in results:
        class_id = detection['class_id']
        bbox = detection['bbox']
        confidence = detection['confidence']
        
        if class_id == 4:  # Person
            persons.append({'bbox': bbox, 'confidence': confidence})
        elif class_id == 2:  # Helmet
            helmets.append({'bbox': bbox, 'confidence': confidence})
        elif class_id in [3, 6, 7]:  # Staff-vest, Other-vest, Visitor-vest
            vests.append({'bbox': bbox, 'confidence': confidence})
        elif class_id == 0:  # Fall-Detected
            falls.append({'bbox': bbox, 'confidence': confidence})
        elif class_id == 1:  # Fire
            fires.append({'bbox': bbox, 'confidence': confidence})
        elif class_id == 5:  # Smoke
            smoke.append({'bbox': bbox, 'confidence': confidence})
    
    # Check for violations
    for person in persons:
        person_bbox = person['bbox']
        
        # Check for helmet
        has_helmet = any(is_inside(helmet['bbox'], person_bbox) for helmet in helmets)
        if not has_helmet:
            violations.append({
                'type': 'NO_HELMET',
                'bbox': person_bbox,
                'confidence': person['confidence'],
                'timestamp': datetime.now().isoformat()
            })
        
        # Check for vest
        has_vest = any(is_inside(vest['bbox'], person_bbox) for vest in vests)
        if not has_vest:
            violations.append({
                'type': 'NO_VEST',
                'bbox': person_bbox,
                'confidence': person['confidence'],
                'timestamp': datetime.now().isoformat()
            })
        
        # Check for fall
        has_fall = any(is_inside(fall['bbox'], person_bbox) for fall in falls)
        if has_fall:
            violations.append({
                'type': 'FALL_DETECTED',
                'bbox': person_bbox,
                'confidence': person['confidence'],
                'timestamp': datetime.now().isoformat()
            })
    
    # Add fire and smoke violations
    for fire in fires:
        violations.append({
            'type': 'FIRE',
            'bbox': fire['bbox'],
            'confidence': fire['confidence'],
            'timestamp': datetime.now().isoformat()
        })
    
    for smoke_detection in smoke:
        violations.append({
            'type': 'SMOKE',
            'bbox': smoke_detection['bbox'],
            'confidence': smoke_detection['confidence'],
            'timestamp': datetime.now().isoformat()
        })
    
    return violations

def is_inside(inner_bbox, outer_bbox):
    """Check if inner bounding box is inside outer bounding box"""
    ix1, iy1, ix2, iy2 = inner_bbox
    ox1, oy1, ox2, oy2 = outer_bbox
    
    return (ix1 >= ox1 and iy1 >= oy1 and ix2 <= ox2 and iy2 <= oy2)

async def violation_monitoring_task():
    """Background task for continuous violation monitoring"""
    while True:
        try:
            if detection_model:
                frame = await camera_manager.get_frame()
                if frame is not None:
                    results = detection_model.detect(frame)
                    violations = process_violations(results, frame)
                    
                    for violation in violations:
                        await violation_logger.log_violation(violation)
                        
                        # Send emergency notifications
                        if violation['type'] in ['FALL_DETECTED', 'FIRE', 'SMOKE']:
                            await notification_manager.send_emergency_alert(
                                violation['type'],
                                f"Location: {violation['bbox']}"
                            )
                    
                    # Broadcast updates
                    await manager.broadcast(json.dumps({
                        "type": "violation_update",
                        "violations": violations,
                        "timestamp": datetime.now().isoformat()
                    }))
            
            await asyncio.sleep(1)  # Check every second
            
        except Exception as e:
            logger.error(f"Error in violation monitoring: {e}")
            await asyncio.sleep(5)

async def daily_report_task():
    """Background task for daily report generation"""
    while True:
        try:
            now = datetime.now()
            if now.hour == 0 and now.minute == 0:  # Midnight
                await report_generator.generate_daily_report()
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Error in daily report task: {e}")
            await asyncio.sleep(300)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="10.4.9.50",
        port=8000,
        reload=True,
        log_level="info"
    )