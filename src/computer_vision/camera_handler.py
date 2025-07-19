"""Camera input handler using OpenCV."""

import cv2
import logging
import threading
from typing import Optional, Tuple, Callable
import numpy as np

from utils.config import CAMERA_DEFAULT_INDEX, CAMERA_FPS


class CameraHandler:
    """Handles camera input and provides frames for processing."""
    
    def __init__(self, camera_index: int = CAMERA_DEFAULT_INDEX):
        self.logger = logging.getLogger(__name__)
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.current_frame: Optional[np.ndarray] = None
        self.frame_lock = threading.Lock()
        self.capture_thread: Optional[threading.Thread] = None
        self.frame_callback: Optional[Callable] = None
        
    def start(self) -> bool:
        """Start camera capture."""
        try:
            # Open camera
            self.cap = cv2.VideoCapture(self.camera_index)
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            # Test camera
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.logger.error("Failed to read from camera")
                self.cap.release()
                return False
                
            self.is_running = True
            
            # Start capture thread
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            self.logger.info(f"Camera started on index {self.camera_index}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start camera: {e}")
            if self.cap:
                self.cap.release()
            return False
            
    def stop(self):
        """Stop camera capture."""
        self.is_running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=1.0)
            
        if self.cap:
            self.cap.release()
            
        self.logger.info("Camera stopped")
        
    def _capture_loop(self):
        """Continuous capture loop running in separate thread."""
        while self.is_running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                
                if ret and frame is not None:
                    # Store frame thread-safely
                    with self.frame_lock:
                        self.current_frame = frame.copy()
                        
                    # Call callback if registered
                    if self.frame_callback:
                        self.frame_callback(frame)
                else:
                    self.logger.warning("Failed to read frame")
            else:
                self.logger.error("Camera not opened")
                self.is_running = False
                
    def get_frame(self) -> Optional[np.ndarray]:
        """Get the latest captured frame."""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None
        
    def get_frame_rgb(self) -> Optional[np.ndarray]:
        """Get the latest frame in RGB format."""
        frame = self.get_frame()
        if frame is not None:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None
        
    def get_frame_size(self) -> Optional[Tuple[int, int]]:
        """Get the frame size (width, height)."""
        if self.cap and self.cap.isOpened():
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (width, height)
        return None
        
    def set_frame_callback(self, callback: Callable):
        """Set a callback function to be called on each new frame."""
        self.frame_callback = callback
        
    def is_active(self) -> bool:
        """Check if camera is actively capturing."""
        return self.is_running and self.cap is not None and self.cap.isOpened()
        
    def switch_camera(self, camera_index: int) -> bool:
        """Switch to a different camera."""
        self.stop()
        self.camera_index = camera_index
        return self.start()
        
    def __del__(self):
        """Cleanup on deletion."""
        self.stop()