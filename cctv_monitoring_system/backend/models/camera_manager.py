import cv2
import numpy as np
import requests
import logging
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

class CameraManager:
    def __init__(self):
        """
        Initialize camera manager for Hikvision IP camera
        """
        self.camera_ip = "10.3.8.111"
        self.username = "admin"
        self.password = "WOWO@2000"
        self.rtsp_url = f"rtsp://{self.username}:{self.password}@{self.camera_ip}:554/Streaming/Channels/101"
        self.http_url = f"http://{self.camera_ip}"
        self.cap = None
        self.connected = False
        self.last_frame = None
        self.last_frame_time = None
        
    async def connect(self) -> bool:
        """
        Connect to Hikvision IP camera
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try RTSP connection first
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            if self.cap.isOpened():
                self.connected = True
                logger.info(f"Connected to Hikvision camera at {self.camera_ip}")
                return True
            else:
                # Try HTTP connection as fallback
                logger.warning("RTSP connection failed, trying HTTP...")
                self.cap = cv2.VideoCapture(f"http://{self.camera_ip}/video")
                
                if self.cap.isOpened():
                    self.connected = True
                    logger.info(f"Connected to Hikvision camera via HTTP at {self.camera_ip}")
                    return True
                else:
                    logger.error("Failed to connect to camera")
                    return False
                    
        except Exception as e:
            logger.error(f"Error connecting to camera: {e}")
            return False
    
    async def get_frame(self) -> Optional[np.ndarray]:
        """
        Get current frame from camera
        
        Returns:
            Frame as numpy array or None if failed
        """
        if not self.connected:
            if not await self.connect():
                return None
        
        try:
            ret, frame = self.cap.read()
            if ret:
                self.last_frame = frame
                self.last_frame_time = datetime.now()
                return frame
            else:
                logger.warning("Failed to read frame from camera")
                return None
                
        except Exception as e:
            logger.error(f"Error getting frame: {e}")
            self.connected = False
            return None
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get camera connection status
        
        Returns:
            Dictionary with camera status information
        """
        return {
            "connected": self.connected,
            "camera_ip": self.camera_ip,
            "last_frame_time": self.last_frame_time.isoformat() if self.last_frame_time else None,
            "rtsp_url": self.rtsp_url,
            "http_url": self.http_url
        }
    
    async def control_ptz(self, action: str, pan: float = 0, tilt: float = 0, zoom: float = 1) -> Dict[str, Any]:
        """
        Control PTZ camera movement
        
        Args:
            action: PTZ action (pan, tilt, zoom, home, preset)
            pan: Pan angle (-1 to 1)
            tilt: Tilt angle (-1 to 1)
            zoom: Zoom level (0.1 to 10)
            
        Returns:
            Dictionary with operation result
        """
        try:
            if action == "pan":
                # Pan control
                url = f"{self.http_url}/ISAPI/PTZCtrl/channels/1/continuous"
                data = {
                    "pan": pan,
                    "tilt": 0,
                    "zoom": 1
                }
                
            elif action == "tilt":
                # Tilt control
                url = f"{self.http_url}/ISAPI/PTZCtrl/channels/1/continuous"
                data = {
                    "pan": 0,
                    "tilt": tilt,
                    "zoom": 1
                }
                
            elif action == "zoom":
                # Zoom control
                url = f"{self.http_url}/ISAPI/PTZCtrl/channels/1/continuous"
                data = {
                    "pan": 0,
                    "tilt": 0,
                    "zoom": zoom
                }
                
            elif action == "home":
                # Go to home position
                url = f"{self.http_url}/ISAPI/PTZCtrl/channels/1/homeposition/goto"
                data = {}
                
            elif action == "stop":
                # Stop all movement
                url = f"{self.http_url}/ISAPI/PTZCtrl/channels/1/continuous"
                data = {
                    "pan": 0,
                    "tilt": 0,
                    "zoom": 1
                }
                
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            # Send HTTP request to camera
            response = requests.post(
                url,
                json=data,
                auth=(self.username, self.password),
                timeout=5
            )
            
            if response.status_code == 200:
                return {"success": True, "action": action, "data": data}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            logger.error(f"Error controlling PTZ: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_snapshot(self) -> Optional[str]:
        """
        Get snapshot from camera
        
        Returns:
            Base64 encoded image or None if failed
        """
        try:
            frame = await self.get_frame()
            if frame is not None:
                # Encode frame to JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                # Convert to base64
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                return image_base64
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting snapshot: {e}")
            return None
    
    async def get_recording_url(self, start_time: str, end_time: str) -> Optional[str]:
        """
        Get recording URL for specific time period
        
        Args:
            start_time: Start time in ISO format
            end_time: End time in ISO format
            
        Returns:
            Recording URL or None if failed
        """
        try:
            # Convert ISO times to camera format
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            
            # Format for Hikvision API
            start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S")
            end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S")
            
            # Construct recording URL
            recording_url = f"{self.http_url}/ISAPI/ContentMgmt/record/search"
            
            # This would require proper Hikvision API implementation
            # For now, return a placeholder
            return f"Recording URL for {start_str} to {end_str}"
            
        except Exception as e:
            logger.error(f"Error getting recording URL: {e}")
            return None
    
    def __del__(self):
        """Cleanup camera connection"""
        if self.cap:
            self.cap.release()