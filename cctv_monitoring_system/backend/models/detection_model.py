import cv2
import numpy as np
from ultralytics import YOLO
import logging
from typing import List, Dict, Any
import torch

logger = logging.getLogger(__name__)

class PPEDetectionModel:
    def __init__(self, model_path: str):
        """
        Initialize PPE detection model
        
        Args:
            model_path: Path to the YOLOv8 model file
        """
        self.model_path = model_path
        self.model = None
        self.class_names = [
            'Fall-Detected',
            'Fire',
            'Helmet',
            'Other-vest',
            'Person',
            'Smoke',
            'Staff-vest',
            'Visitor-vest'
        ]
        self.load_model()
    
    def load_model(self):
        """Load the YOLOv8 model"""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run detection on a frame
        
        Args:
            frame: Input image frame as numpy array
            
        Returns:
            List of detection results with bbox, class_id, confidence
        """
        if self.model is None:
            logger.error("Model not loaded")
            return []
        
        try:
            # Run inference
            results = self.model(frame, verbose=False)
            
            detections = []
            
            for result in results:
                if result.boxes is not None:
                    boxes = result.boxes
                    
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Get class and confidence
                        class_id = int(box.cls[0].cpu().numpy())
                        confidence = float(box.conf[0].cpu().numpy())
                        
                        # Only include detections with confidence > 0.5
                        if confidence > 0.5:
                            detections.append({
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'class_id': class_id,
                                'class_name': self.class_names[class_id],
                                'confidence': confidence
                            })
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return []
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw detection bounding boxes on frame
        
        Args:
            frame: Input frame
            detections: List of detection results
            
        Returns:
            Frame with bounding boxes drawn
        """
        frame_copy = frame.copy()
        
        # Color mapping for different classes
        colors = {
            'Fall-Detected': (0, 0, 255),    # Red
            'Fire': (0, 165, 255),           # Orange
            'Helmet': (0, 255, 0),           # Green
            'Other-vest': (255, 0, 0),       # Blue
            'Person': (255, 255, 0),         # Cyan
            'Smoke': (128, 128, 128),        # Gray
            'Staff-vest': (255, 0, 255),     # Magenta
            'Visitor-vest': (0, 255, 255)    # Yellow
        }
        
        for detection in detections:
            bbox = detection['bbox']
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            # Get color for this class
            color = colors.get(class_name, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(frame_copy, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Draw label background
            cv2.rectangle(frame_copy, 
                         (bbox[0], bbox[1] - label_size[1] - 10),
                         (bbox[0] + label_size[0], bbox[1]),
                         color, -1)
            
            # Draw label text
            cv2.putText(frame_copy, label, (bbox[0], bbox[1] - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame_copy
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'model_path': self.model_path,
            'class_names': self.class_names,
            'num_classes': len(self.class_names),
            'loaded': self.model is not None
        }