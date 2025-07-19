"""Simplified version of the Thought Bubble Camera App for testing."""

import cv2
import pygame
import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from computer_vision.detector import PersonDetector
from computer_vision.simple_tracker import SimpleTracker
from bubble_system.bubble_renderer import BubbleRenderer
from utils.logging_setup import setup_logging

# Setup logging
logger = setup_logging(logging.INFO)

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 30

def main():
    """Main function for simplified app."""
    logger.info("Starting simplified Thought Bubble Camera")
    
    # Create Pygame window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Thought Bubble Camera - Simplified")
    clock = pygame.time.Clock()
    
    # Initialize components
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Failed to open camera!")
        return
        
    detector = PersonDetector()
    tracker = SimpleTracker()
    bubble_renderer = BubbleRenderer()
    
    # State variables
    running = True
    fullscreen = False
    show_bubbles = True
    show_debug = False
    frame_count = 0
    
    logger.info("Press F11 for fullscreen, B to toggle bubbles, D for debug, Q to quit")
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        logger.info("Entered fullscreen mode")
                    else:
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                        logger.info("Exited fullscreen mode")
                elif event.key == pygame.K_ESCAPE and fullscreen:
                    fullscreen = False
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                elif event.key == pygame.K_b:
                    show_bubbles = not show_bubbles
                    logger.info(f"Bubbles: {'ON' if show_bubbles else 'OFF'}")
                elif event.key == pygame.K_d:
                    show_debug = not show_debug
                    logger.info(f"Debug: {'ON' if show_debug else 'OFF'}")
        
        # Capture frame
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to read frame")
            continue
            
        # Resize frame to fit screen
        frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Detect people every frame for better stability
        if True:  # frame_count % 2 == 0:
            detections = detector.detect(frame)
            
            # Update tracker with detections
            tracked_persons = tracker.update(detections)
            
            if tracked_persons:
                logger.debug(f"Tracking {len(tracked_persons)} people")
                
                # Update bubbles
                if show_bubbles:
                    active_ids = []
                    for person_id, (detection, thought_index) in tracked_persons.items():
                        active_ids.append(person_id)
                        
                        # Create or update bubble
                        if person_id not in bubble_renderer.bubbles:
                            # Create new bubble with consistent thought
                            bubble_renderer.create_bubble(
                                person_id,
                                detection.head_position,
                                thought_index=thought_index
                            )
                            logger.info(f"Created bubble for {person_id} with thought index {thought_index}")
                        else:
                            # Just update position, keep same thought
                            bubble_renderer.update_bubble_position(
                                person_id,
                                detection.head_position
                            )
                    
                    # Remove bubbles for missing people
                    for person_id in list(bubble_renderer.bubbles.keys()):
                        if person_id not in active_ids:
                            bubble_renderer.remove_bubble(person_id)
                            logger.info(f"Removed bubble for {person_id}")
            
            # Draw debug info with original detections
            if show_debug:
                detector.draw_detections(frame, detections)
        
        # Convert frame to RGB and create surface
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        
        # Draw everything
        screen.blit(frame_surface, (0, 0))
        
        # Update and draw bubbles
        if show_bubbles:
            bubble_renderer.update()
            bubble_renderer.draw(screen)
        
        # Draw UI text
        font = pygame.font.Font(None, 24)
        y_pos = 10
        for text, color in [
            (f"FPS: {clock.get_fps():.1f}", (0, 255, 0)),
            (f"Bubbles: {'ON' if show_bubbles else 'OFF'} (B)", (255, 255, 255)),
            (f"Debug: {'ON' if show_debug else 'OFF'} (D)", (255, 255, 255)),
            (f"Fullscreen: F11", (255, 255, 255)),
            (f"Detections: {bubble_renderer.get_bubble_count()}", (255, 255, 0))
        ]:
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (10, y_pos))
            y_pos += 30
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
        frame_count += 1
    
    # Cleanup
    cap.release()
    pygame.quit()
    logger.info("Application closed")

if __name__ == "__main__":
    main()