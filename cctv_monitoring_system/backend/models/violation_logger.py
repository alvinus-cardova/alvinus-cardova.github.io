import cv2
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ViolationLogger:
    def __init__(self, logs_dir: str = "logs", screenshots_dir: str = "data/screenshots"):
        """
        Initialize violation logger
        
        Args:
            logs_dir: Directory for log files
            screenshots_dir: Directory for violation screenshots
        """
        self.logs_dir = Path(logs_dir)
        self.screenshots_dir = Path(screenshots_dir)
        
        # Create directories if they don't exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Violation counter
        self.violation_count = 0
        
    async def log_violation(self, violation_data: Dict[str, Any], frame: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Log a violation with screenshot and metadata
        
        Args:
            violation_data: Dictionary containing violation information
            frame: Optional frame to capture screenshot from
            
        Returns:
            Dictionary with logging results
        """
        try:
            timestamp = datetime.now()
            violation_id = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{self.violation_count}"
            self.violation_count += 1
            
            # Create violation record
            violation_record = {
                'id': violation_id,
                'type': violation_data['type'],
                'timestamp': timestamp.isoformat(),
                'bbox': violation_data['bbox'],
                'confidence': violation_data['confidence'],
                'camera_id': violation_data.get('camera_id', 'main'),
                'location': violation_data.get('location', 'unknown'),
                'screenshot_path': None,
                'processed': 0
            }
            
            # Capture screenshot if frame is provided
            if frame is not None:
                screenshot_path = await self._capture_screenshot(
                    frame, violation_data['bbox'], violation_id
                )
                violation_record['screenshot_path'] = str(screenshot_path)
            
            # Save violation record to JSON log
            await self._save_violation_record(violation_record)
            
            # Log to console
            logger.info(f"Violation logged: {violation_data['type']} at {timestamp}")
            
            return {
                'success': True,
                'violation_id': violation_id,
                'screenshot_path': violation_record['screenshot_path']
            }
            
        except Exception as e:
            logger.error(f"Error logging violation: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _capture_screenshot(self, frame: np.ndarray, bbox: list, violation_id: str) -> Path:
        """
        Capture screenshot of violation area
        
        Args:
            frame: Input frame
            bbox: Bounding box coordinates [x1, y1, x2, y2]
            violation_id: Unique violation ID
            
        Returns:
            Path to saved screenshot
        """
        try:
            # Extract region around violation
            x1, y1, x2, y2 = bbox
            
            # Add padding around the bounding box
            padding = 50
            h, w = frame.shape[:2]
            
            # Ensure coordinates are within frame bounds
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(w, x2 + padding)
            y2 = min(h, y2 + padding)
            
            # Extract region
            violation_region = frame[y1:y2, x1:x2]
            
            # Draw bounding box on the region
            cv2.rectangle(violation_region, (padding, padding), 
                         (x2-x1-padding, y2-y1-padding), (0, 0, 255), 2)
            
            # Save screenshot
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"violation_{violation_id}_{timestamp_str}.jpg"
            screenshot_path = self.screenshots_dir / filename
            
            cv2.imwrite(str(screenshot_path), violation_region)
            
            logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            raise
    
    async def _save_violation_record(self, violation_record: Dict[str, Any]):
        """
        Save violation record to JSON log file
        
        Args:
            violation_record: Violation record to save
        """
        try:
            # Create daily log file
            date_str = datetime.now().strftime('%Y-%m-%d')
            log_file = self.logs_dir / f"violations_{date_str}.json"
            
            # Load existing records or create new file
            if log_file.exists():
                with open(log_file, 'r') as f:
                    records = json.load(f)
            else:
                records = []
            
            # Add new record
            records.append(violation_record)
            
            # Save back to file
            with open(log_file, 'w') as f:
                json.dump(records, f, indent=2)
            
            logger.info(f"Violation record saved to {log_file}")
            
        except Exception as e:
            logger.error(f"Error saving violation record: {e}")
            raise
    
    async def get_violation_logs(self, date: Optional[str] = None, 
                               violation_type: Optional[str] = None) -> list:
        """
        Get violation logs with optional filters
        
        Args:
            date: Date filter (YYYY-MM-DD format)
            violation_type: Type of violation to filter
            
        Returns:
            List of violation records
        """
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            log_file = self.logs_dir / f"violations_{date}.json"
            
            if not log_file.exists():
                return []
            
            with open(log_file, 'r') as f:
                records = json.load(f)
            
            # Apply filters
            if violation_type:
                records = [r for r in records if r['type'] == violation_type]
            
            return records
            
        except Exception as e:
            logger.error(f"Error reading violation logs: {e}")
            return []
    
    async def get_violation_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get violation statistics for the specified number of days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with violation statistics
        """
        try:
            stats = {
                'total_violations': 0,
                'violations_by_type': {},
                'violations_by_date': {},
                'most_common_locations': {},
                'average_confidence': 0.0
            }
            
            total_confidence = 0.0
            confidence_count = 0
            
            # Analyze each day
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                records = await self.get_violation_logs(date)
                
                for record in records:
                    # Count total violations
                    stats['total_violations'] += 1
                    
                    # Count by type
                    violation_type = record['type']
                    stats['violations_by_type'][violation_type] = \
                        stats['violations_by_type'].get(violation_type, 0) + 1
                    
                    # Count by date
                    stats['violations_by_date'][date] = \
                        stats['violations_by_date'].get(date, 0) + 1
                    
                    # Count by location
                    location = record.get('location', 'unknown')
                    stats['most_common_locations'][location] = \
                        stats['most_common_locations'].get(location, 0) + 1
                    
                    # Calculate average confidence
                    confidence = record.get('confidence', 0.0)
                    total_confidence += confidence
                    confidence_count += 1
            
            # Calculate average confidence
            if confidence_count > 0:
                stats['average_confidence'] = total_confidence / confidence_count
            
            # Sort by frequency
            stats['violations_by_type'] = dict(
                sorted(stats['violations_by_type'].items(), 
                      key=lambda x: x[1], reverse=True)
            )
            stats['most_common_locations'] = dict(
                sorted(stats['most_common_locations'].items(), 
                      key=lambda x: x[1], reverse=True)
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    async def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Clean up old log files and screenshots
        
        Args:
            days_to_keep: Number of days of logs to keep
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Clean up log files
            for log_file in self.logs_dir.glob("violations_*.json"):
                try:
                    # Extract date from filename
                    date_str = log_file.stem.split('_')[1]
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    if file_date < cutoff_date:
                        log_file.unlink()
                        logger.info(f"Deleted old log file: {log_file}")
                except Exception as e:
                    logger.warning(f"Error processing log file {log_file}: {e}")
            
            # Clean up screenshots
            for screenshot in self.screenshots_dir.glob("*.jpg"):
                try:
                    # Extract date from filename
                    parts = screenshot.stem.split('_')
                    if len(parts) >= 3:
                        date_str = parts[1]
                        file_date = datetime.strptime(date_str, '%Y%m%d')
                        
                        if file_date < cutoff_date:
                            screenshot.unlink()
                            logger.info(f"Deleted old screenshot: {screenshot}")
                except Exception as e:
                    logger.warning(f"Error processing screenshot {screenshot}: {e}")
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_logger_status(self) -> Dict[str, Any]:
        """
        Get logger status information
        
        Returns:
            Dictionary with logger status
        """
        try:
            # Count log files
            log_files = list(self.logs_dir.glob("violations_*.json"))
            
            # Count screenshots
            screenshots = list(self.screenshots_dir.glob("*.jpg"))
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in log_files + screenshots)
            
            return {
                'logs_directory': str(self.logs_dir),
                'screenshots_directory': str(self.screenshots_dir),
                'log_files_count': len(log_files),
                'screenshots_count': len(screenshots),
                'total_size_mb': total_size / (1024 * 1024),
                'violation_count': self.violation_count
            }
            
        except Exception as e:
            logger.error(f"Error getting logger status: {e}")
            return {}