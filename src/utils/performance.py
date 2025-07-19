"""Performance monitoring and optimization utilities."""

import time
import threading
from collections import deque
from typing import Dict, Optional
import logging


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self, history_size: int = 100):
        self.logger = logging.getLogger(__name__)
        self.history_size = history_size
        
        # Timing data
        self.frame_times = deque(maxlen=history_size)
        self.detection_times = deque(maxlen=history_size)
        self.render_times = deque(maxlen=history_size)
        
        # Counters
        self.frame_count = 0
        self.detection_count = 0
        self.dropped_frames = 0
        
        # Current metrics
        self.current_fps = 0.0
        self.avg_detection_time = 0.0
        self.avg_render_time = 0.0
        
        # Timing helpers
        self._timers: Dict[str, float] = {}
        self._lock = threading.Lock()
        
    def start_timer(self, name: str):
        """Start a named timer."""
        with self._lock:
            self._timers[name] = time.time()
            
    def end_timer(self, name: str) -> float:
        """End a named timer and return elapsed time."""
        with self._lock:
            if name not in self._timers:
                return 0.0
                
            elapsed = time.time() - self._timers[name]
            del self._timers[name]
            
            # Store in appropriate history
            if name == "frame":
                self.frame_times.append(elapsed)
                self.frame_count += 1
            elif name == "detection":
                self.detection_times.append(elapsed)
                self.detection_count += 1
            elif name == "render":
                self.render_times.append(elapsed)
                
            return elapsed
            
    def record_dropped_frame(self):
        """Record a dropped frame."""
        self.dropped_frames += 1
        
    def update_metrics(self):
        """Update calculated metrics."""
        with self._lock:
            # Calculate FPS from frame times
            if len(self.frame_times) > 0:
                avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                self.current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
                
            # Calculate average times
            if len(self.detection_times) > 0:
                self.avg_detection_time = sum(self.detection_times) / len(self.detection_times)
                
            if len(self.render_times) > 0:
                self.avg_render_time = sum(self.render_times) / len(self.render_times)
                
    def get_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""
        self.update_metrics()
        
        return {
            "fps": self.current_fps,
            "avg_detection_ms": self.avg_detection_time * 1000,
            "avg_render_ms": self.avg_render_time * 1000,
            "frame_count": self.frame_count,
            "detection_count": self.detection_count,
            "dropped_frames": self.dropped_frames,
            "drop_rate": self.dropped_frames / max(1, self.frame_count)
        }
        
    def log_metrics(self):
        """Log current metrics."""
        metrics = self.get_metrics()
        self.logger.info(
            f"Performance - FPS: {metrics['fps']:.1f}, "
            f"Detection: {metrics['avg_detection_ms']:.1f}ms, "
            f"Render: {metrics['avg_render_ms']:.1f}ms, "
            f"Dropped: {metrics['dropped_frames']} ({metrics['drop_rate']*100:.1f}%)"
        )
        
    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self.frame_times.clear()
            self.detection_times.clear()
            self.render_times.clear()
            self.frame_count = 0
            self.detection_count = 0
            self.dropped_frames = 0
            self._timers.clear()


class FrameSkipper:
    """Intelligent frame skipping based on performance."""
    
    def __init__(self, target_fps: int = 30, min_skip: int = 1, max_skip: int = 5):
        self.target_fps = target_fps
        self.min_skip = min_skip
        self.max_skip = max_skip
        self.current_skip = min_skip
        self.frame_count = 0
        
    def should_process(self) -> bool:
        """Determine if current frame should be processed."""
        self.frame_count += 1
        return self.frame_count % self.current_skip == 0
        
    def adjust_skip_rate(self, current_fps: float):
        """Adjust skip rate based on current FPS."""
        if current_fps < self.target_fps * 0.8:
            # Performance is low, increase skip
            self.current_skip = min(self.current_skip + 1, self.max_skip)
        elif current_fps > self.target_fps * 1.1:
            # Performance is good, decrease skip
            self.current_skip = max(self.current_skip - 1, self.min_skip)
            
    def get_skip_rate(self) -> int:
        """Get current skip rate."""
        return self.current_skip