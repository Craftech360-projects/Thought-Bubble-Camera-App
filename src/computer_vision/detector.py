"""Person detection using MediaPipe."""

import cv2
import mediapipe as mp
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from utils.config import BUBBLE_OFFSET_Y


@dataclass
class Detection:
    """Represents a detected person."""
    id: str
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    head_position: Tuple[int, int]  # x, y
    confidence: float
    

class PersonDetector:
    """Detects people and their head positions using MediaPipe."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize MediaPipe Face Detection as primary detector
        self.mp_face = mp.solutions.face_detection
        self.face_detection = self.mp_face.FaceDetection(
            model_selection=1,  # 1 for full range detection (better for far faces)
            min_detection_confidence=0.3  # Lower threshold for better detection
        )
        
        self.logger.info("Person detector initialized with MediaPipe")
        
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Detect people in frame and return their positions."""
        if frame is None:
            return []
            
        detections = []
        
        # Use face detection as primary (supports multiple people)
        face_detections = self._detect_with_face(frame)
        if face_detections:
            detections.extend(face_detections)
        else:
            # Fallback to pose detection for single person
            pose_detections = self._detect_with_pose(frame)
            detections.extend(pose_detections)
            
        return detections
        
    def _detect_with_pose(self, frame: np.ndarray) -> List[Detection]:
        """Detect people using pose estimation."""
        detections = []
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            h, w = frame.shape[:2]
            
            # Get key landmarks
            landmarks = results.pose_landmarks.landmark
            
            # Calculate head position (average of nose, left eye, right eye)
            nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
            left_eye = landmarks[self.mp_pose.PoseLandmark.LEFT_EYE]
            right_eye = landmarks[self.mp_pose.PoseLandmark.RIGHT_EYE]
            
            head_x = int((nose.x + left_eye.x + right_eye.x) / 3 * w)
            head_y = int((nose.y + left_eye.y + right_eye.y) / 3 * h)
            
            # Calculate bounding box from all visible landmarks
            visible_landmarks = [lm for lm in landmarks if lm.visibility > 0.5]
            if visible_landmarks:
                xs = [int(lm.x * w) for lm in visible_landmarks]
                ys = [int(lm.y * h) for lm in visible_landmarks]
                
                x_min, x_max = min(xs), max(xs)
                y_min, y_max = min(ys), max(ys)
                
                # Add padding
                padding = 50
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(w, x_max + padding)
                y_max = min(h, y_max + padding)
                
                detection = Detection(
                    id="pose_0",  # Single person for now
                    bbox=(x_min, y_min, x_max - x_min, y_max - y_min),
                    head_position=(head_x, head_y - BUBBLE_OFFSET_Y),
                    confidence=0.8
                )
                detections.append(detection)
                
        return detections
        
    def _detect_with_face(self, frame: np.ndarray) -> List[Detection]:
        """Detect people using face detection."""
        detections = []
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)
        
        if results.detections:
            h, w = frame.shape[:2]
            
            for i, detection in enumerate(results.detections):
                bbox = detection.location_data.relative_bounding_box
                
                # Convert to pixel coordinates
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Ensure bounds are valid
                x = max(0, x)
                y = max(0, y)
                width = min(width, w - x)
                height = min(height, h - y)
                
                # Head position is top center of face
                head_x = x + width // 2
                head_y = y
                
                # Extend bbox to include upper body estimate
                body_y = y + height
                body_height = height * 3  # Estimate body as 3x face height
                
                det = Detection(
                    id=f"face_{i}",
                    bbox=(x, y, width, min(body_height, h - y)),
                    head_position=(head_x, head_y - BUBBLE_OFFSET_Y),
                    confidence=detection.score[0] if detection.score else 0.5
                )
                detections.append(det)
                
        return detections
        
    def draw_detections(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """Draw detection boxes and points on frame for debugging."""
        for det in detections:
            # Draw bounding box
            x, y, w, h = det.bbox
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw head position
            cv2.circle(frame, det.head_position, 5, (0, 0, 255), -1)
            
            # Draw ID and confidence
            text = f"{det.id} ({det.confidence:.2f})"
            cv2.putText(frame, text, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                       
        return frame
        
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'pose'):
            self.pose.close()
        if hasattr(self, 'face_detection'):
            self.face_detection.close()