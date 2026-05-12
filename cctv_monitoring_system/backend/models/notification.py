import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        """
        Initialize notification manager for emergency alerts
        """
        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_username = os.getenv("EMAIL_USERNAME", "admin@company.com")
        self.email_password = os.getenv("EMAIL_PASSWORD", "password")
        
        # WhatsApp configuration (Twilio)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER", "")
        
        # Emergency contact numbers
        self.emergency_contacts = {
            "medical_team": ["+1234567890", "+1234567891"],
            "security_team": ["+1234567892", "+1234567893"],
            "management": ["+1234567894", "+1234567895"]
        }
        
        # Sound alert configuration
        self.sound_alerts = {
            "FALL_DETECTED": "medical_siren.wav",
            "FIRE": "evacuation_alarm.wav",
            "SMOKE": "evacuation_alarm.wav",
            "NO_HELMET": "light_warning.wav",
            "NO_VEST": "light_warning.wav"
        }
        
        # Notification templates
        self.templates = {
            "FALL_DETECTED": {
                "subject": "🚨 FALL DETECTED - Emergency Response Required",
                "body": """
                EMERGENCY ALERT: Fall detected at {location}
                
                Time: {timestamp}
                Camera: {camera_id}
                Confidence: {confidence}%
                
                Immediate action required:
                1. Send medical team to location
                2. Check for injuries
                3. Secure the area
                
                This is an automated emergency alert.
                """,
                "priority": "high"
            },
            "FIRE": {
                "subject": "🔥 FIRE DETECTED - Evacuation Required",
                "body": """
                EMERGENCY ALERT: Fire detected at {location}
                
                Time: {timestamp}
                Camera: {camera_id}
                Confidence: {confidence}%
                
                Immediate action required:
                1. Activate fire alarm
                2. Evacuate all personnel
                3. Contact fire department
                4. Check for trapped individuals
                
                This is an automated emergency alert.
                """,
                "priority": "critical"
            },
            "SMOKE": {
                "subject": "💨 SMOKE DETECTED - Investigation Required",
                "body": """
                ALERT: Smoke detected at {location}
                
                Time: {timestamp}
                Camera: {camera_id}
                Confidence: {confidence}%
                
                Action required:
                1. Investigate source of smoke
                2. Prepare for potential evacuation
                3. Monitor for fire development
                
                This is an automated alert.
                """,
                "priority": "medium"
            },
            "NO_HELMET": {
                "subject": "⚠️ PPE VIOLATION - No Helmet",
                "body": """
                PPE Violation: Worker without helmet at {location}
                
                Time: {timestamp}
                Camera: {camera_id}
                
                Action required:
                1. Notify supervisor
                2. Provide helmet to worker
                3. Document violation
                
                This is an automated alert.
                """,
                "priority": "low"
            },
            "NO_VEST": {
                "subject": "⚠️ PPE VIOLATION - No Safety Vest",
                "body": """
                PPE Violation: Worker without safety vest at {location}
                
                Time: {timestamp}
                Camera: {camera_id}
                
                Action required:
                1. Notify supervisor
                2. Provide safety vest to worker
                3. Document violation
                
                This is an automated alert.
                """,
                "priority": "low"
            }
        }
    
    async def send_emergency_alert(self, violation_type: str, location: str, 
                                 camera_id: str = "main", confidence: float = 0.0,
                                 screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Send emergency alert for violation
        
        Args:
            violation_type: Type of violation
            location: Location of violation
            camera_id: Camera ID
            confidence: Detection confidence
            screenshot_path: Path to violation screenshot
            
        Returns:
            Dictionary with notification results
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get template for violation type
            template = self.templates.get(violation_type, {
                "subject": f"Alert: {violation_type}",
                "body": f"Violation detected at {location}",
                "priority": "medium"
            })
            
            # Format message
            message_body = template["body"].format(
                location=location,
                timestamp=timestamp,
                camera_id=camera_id,
                confidence=confidence * 100
            )
            
            results = {
                "email_sent": False,
                "whatsapp_sent": False,
                "sound_alert": False,
                "errors": []
            }
            
            # Send email notification
            try:
                await self._send_email_alert(
                    template["subject"],
                    message_body,
                    screenshot_path
                )
                results["email_sent"] = True
            except Exception as e:
                results["errors"].append(f"Email error: {str(e)}")
            
            # Send WhatsApp notification for high priority alerts
            if template["priority"] in ["high", "critical"]:
                try:
                    await self._send_whatsapp_alert(
                        violation_type,
                        message_body,
                        location
                    )
                    results["whatsapp_sent"] = True
                except Exception as e:
                    results["errors"].append(f"WhatsApp error: {str(e)}")
            
            # Trigger sound alert
            try:
                await self._play_sound_alert(violation_type)
                results["sound_alert"] = True
            except Exception as e:
                results["errors"].append(f"Sound alert error: {str(e)}")
            
            logger.info(f"Emergency alert sent for {violation_type}: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error sending emergency alert: {e}")
            return {"error": str(e)}
    
    async def _send_email_alert(self, subject: str, body: str, 
                               screenshot_path: Optional[str] = None) -> bool:
        """
        Send email alert
        
        Args:
            subject: Email subject
            body: Email body
            screenshot_path: Path to screenshot attachment
            
        Returns:
            True if sent successfully
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = ", ".join(self.emergency_contacts["management"])
            msg['Subject'] = subject
            
            # Add text body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add screenshot if provided
            if screenshot_path and os.path.exists(screenshot_path):
                with open(screenshot_path, "rb") as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', '<violation_screenshot>')
                    msg.attach(img)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_username, self.email_password)
                server.send_message(msg)
            
            logger.info("Email alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            raise
    
    async def _send_whatsapp_alert(self, violation_type: str, message: str, 
                                  location: str) -> bool:
        """
        Send WhatsApp alert using Twilio
        
        Args:
            violation_type: Type of violation
            message: Alert message
            location: Location of violation
            
        Returns:
            True if sent successfully
        """
        try:
            if not self.twilio_account_sid or not self.twilio_auth_token:
                logger.warning("Twilio credentials not configured")
                return False
            
            # Determine which contacts to notify based on violation type
            if violation_type in ["FALL_DETECTED"]:
                contacts = self.emergency_contacts["medical_team"]
            elif violation_type in ["FIRE", "SMOKE"]:
                contacts = self.emergency_contacts["security_team"]
            else:
                contacts = self.emergency_contacts["management"]
            
            # Send to each contact
            for contact in contacts:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
                
                data = {
                    "From": f"whatsapp:{self.twilio_phone_number}",
                    "To": f"whatsapp:{contact}",
                    "Body": f"🚨 {violation_type}\n{message}\nLocation: {location}"
                }
                
                response = requests.post(
                    url,
                    data=data,
                    auth=(self.twilio_account_sid, self.twilio_auth_token)
                )
                
                if response.status_code == 201:
                    logger.info(f"WhatsApp alert sent to {contact}")
                else:
                    logger.error(f"Failed to send WhatsApp to {contact}: {response.text}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp alert: {e}")
            raise
    
    async def _play_sound_alert(self, violation_type: str) -> bool:
        """
        Play sound alert for violation
        
        Args:
            violation_type: Type of violation
            
        Returns:
            True if played successfully
        """
        try:
            sound_file = self.sound_alerts.get(violation_type, "default_alert.wav")
            sound_path = f"assets/sounds/{sound_file}"
            
            if os.path.exists(sound_path):
                # Use system command to play sound
                import subprocess
                subprocess.run(["aplay", sound_path], capture_output=True)
                logger.info(f"Sound alert played: {sound_file}")
                return True
            else:
                logger.warning(f"Sound file not found: {sound_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error playing sound alert: {e}")
            return False
    
    async def send_daily_report(self, report_path: str, date: str) -> bool:
        """
        Send daily compliance report
        
        Args:
            report_path: Path to PDF report
            date: Report date
            
        Returns:
            True if sent successfully
        """
        try:
            subject = f"Daily PPE Compliance Report - {date}"
            body = f"""
            Daily PPE Compliance Report
            
            Date: {date}
            
            Please find attached the daily compliance report for {date}.
            
            This report includes:
            - Violation summaries
            - Compliance statistics
            - Heatmap analysis
            - Recommendations
            
            Best regards,
            CCTV Monitoring System
            """
            
            await self._send_email_alert(subject, body, report_path)
            return True
            
        except Exception as e:
            logger.error(f"Error sending daily report: {e}")
            return False
    
    def get_notification_status(self) -> Dict[str, Any]:
        """
        Get notification system status
        
        Returns:
            Dictionary with notification system status
        """
        return {
            "email_configured": bool(self.email_username and self.email_password),
            "whatsapp_configured": bool(self.twilio_account_sid and self.twilio_auth_token),
            "emergency_contacts": {
                "medical_team": len(self.emergency_contacts["medical_team"]),
                "security_team": len(self.emergency_contacts["security_team"]),
                "management": len(self.emergency_contacts["management"])
            },
            "sound_alerts": list(self.sound_alerts.keys()),
            "templates": list(self.templates.keys())
        }