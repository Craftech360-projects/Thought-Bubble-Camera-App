"""Overlay renderer that combines camera feed with bubbles."""

import pygame
import cv2
import numpy as np
import logging
from typing import Optional, Tuple

from bubble_system.bubble_renderer import BubbleRenderer
from computer_vision.camera_handler import CameraHandler
from computer_vision.detector import PersonDetector
from computer_vision.simple_tracker import SimpleTracker
from utils.config import FRAME_SKIP


class OverlayRenderer:
    """Manages the overlay of bubbles on camera feed."""
    
    def __init__(self, screen: pygame.Surface):
        self.logger = logging.getLogger(__name__)
        self.screen = screen
        self.screen_size = screen.get_size()
        
        # Initialize components
        self.camera_handler = CameraHandler()
        self.person_detector = PersonDetector()
        self.person_tracker = SimpleTracker()
        self.bubble_renderer = BubbleRenderer()
        
        # Performance optimization
        self.frame_count = 0
        self.detection_active = True
        
        # Debug mode
        self.show_debug = False
        
    def start_camera(self) -> bool:
        """Start the camera capture."""
        success = self.camera_handler.start()
        if success:
            self.logger.info("Camera started successfully")
        else:
            self.logger.error("Failed to start camera")
        return success
        
    def stop_camera(self):
        """Stop the camera capture."""
        self.camera_handler.stop()
        self.person_tracker.reset()
        self.bubble_renderer.clear_all()
        
    def toggle_debug(self):
        """Toggle debug visualization."""
        self.show_debug = not self.show_debug
        self.logger.info(f"Debug mode: {self.show_debug}")
        
    def render(self, show_bubbles: bool = True):
        """Render the camera feed with bubble overlay."""
        # Get camera frame
        frame = self.camera_handler.get_frame_rgb()
        
        if frame is not None:
            # Resize frame to fit screen
            frame_height, frame_width = frame.shape[:2]
            screen_width, screen_height = self.screen_size
            
            # Calculate scaling to fit screen while maintaining aspect ratio
            scale_x = screen_width / frame_width
            scale_y = screen_height / frame_height
            scale = min(scale_x, scale_y)
            
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            
            # Resize frame
            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            # Center frame on screen
            x_offset = (screen_width - new_width) // 2
            y_offset = (screen_height - new_height) // 2
            
            # Process detections (with frame skipping)
            if show_bubbles and self.detection_active:
                self.frame_count += 1
                
                if self.frame_count % FRAME_SKIP == 0:
                    # Detect people
                    detections = self.person_detector.detect(frame)
                    
                    # Track people
                    tracked_persons = self.person_tracker.update(detections)
                    
                    # Update bubbles
                    self._update_bubbles(tracked_persons, scale, x_offset, y_offset)
                    
                    # Draw debug info if enabled
                    if self.show_debug:
                        resized_frame = self._draw_debug_info(
                            resized_frame, detections, scale
                        )
                        
            # Convert frame to Pygame surface
            frame_surface = pygame.surfarray.make_surface(
                np.transpose(resized_frame, (1, 0, 2))
            )
            
            # Draw frame
            self.screen.fill((0, 0, 0))
            self.screen.blit(frame_surface, (x_offset, y_offset))
            
            # Draw bubbles
            if show_bubbles:
                self.bubble_renderer.update()
                self.bubble_renderer.handle_collisions()
                self.bubble_renderer.draw(self.screen)
        else:
            # No camera feed - show placeholder
            self._draw_no_camera()
            
    def _update_bubbles(self, tracked_persons, scale, x_offset, y_offset):
        """Update bubble positions based on tracked persons."""
        active_person_ids = set()
        
        for person_id, (detection, thought_index) in tracked_persons.items():
            active_person_ids.add(person_id)
            
            # Use detection head position directly
            head_pos = detection.head_position
            if head_pos:
                # Scale and offset position to screen coordinates
                screen_x = int(head_pos[0] * scale) + x_offset
                screen_y = int(head_pos[1] * scale) + y_offset
                
                # Create or update bubble
                if person_id not in self.bubble_renderer.bubbles:
                    self.bubble_renderer.create_bubble(
                        person_id, 
                        (screen_x, screen_y),
                        thought_index=thought_index
                    )
                else:
                    self.bubble_renderer.update_bubble_position(
                        person_id,
                        (screen_x, screen_y)
                    )
                    
        # Remove bubbles for lost persons
        current_bubble_ids = set(self.bubble_renderer.bubbles.keys())
        for person_id in current_bubble_ids - active_person_ids:
            self.bubble_renderer.remove_bubble(person_id)
            
    def _draw_debug_info(self, frame, detections, scale):
        """Draw debug information on frame."""
        for det in detections:
            # Scale detection coordinates
            x, y, w, h = det.bbox
            x = int(x * scale)
            y = int(y * scale)
            w = int(w * scale)
            h = int(h * scale)
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw head position
            head_x = int(det.head_position[0] * scale)
            head_y = int(det.head_position[1] * scale)
            cv2.circle(frame, (head_x, head_y), 5, (0, 0, 255), -1)
            
            # Draw ID and confidence
            text = f"{det.confidence:.2f}"
            cv2.putText(frame, text, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                       
        return frame
        
    def _draw_no_camera(self):
        """Draw placeholder when no camera available."""
        self.screen.fill((30, 30, 30))
        font = pygame.font.Font(None, 48)
        text = font.render("No Camera Feed", True, (100, 100, 100))
        text_rect = text.get_rect(center=(self.screen_size[0] // 2, self.screen_size[1] // 2))
        self.screen.blit(text, text_rect)
        
    def cleanup(self):
        """Clean up resources."""
        self.camera_handler.stop()
        self.person_detector.cleanup()
        self.logger.info("Overlay renderer cleaned up")