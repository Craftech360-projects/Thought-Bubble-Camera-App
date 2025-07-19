"""Bubble rendering system that manages multiple bubbles."""

import pygame
import logging
from typing import Dict, List, Tuple, Optional
import random

from bubble_system.bubble import Bubble
from bubble_system.thought_generator import ThoughtGenerator
from bubble_system.bubble_pool import BubblePool


class BubbleRenderer:
    """Manages and renders multiple thought bubbles."""
    
    def __init__(self, use_pooling: bool = True):
        self.logger = logging.getLogger(__name__)
        self.bubbles: Dict[str, Bubble] = {}
        self.thought_generator = ThoughtGenerator()
        self.use_pooling = use_pooling
        
        # Initialize bubble pool if enabled
        if self.use_pooling:
            self.bubble_pool = BubblePool()
        else:
            self.bubble_pool = None
        
    def create_bubble(self, person_id: str, position: Tuple[int, int], 
                     text: Optional[str] = None, thought_index: Optional[int] = None) -> Bubble:
        """Create a new bubble for a person."""
        # Use provided text or specific/random thought
        if text is None:
            if thought_index is not None and 0 <= thought_index < len(self.thought_generator.thoughts):
                text = self.thought_generator.thoughts[thought_index]
            else:
                text = self.thought_generator.get_random_thought()
            
        # Remove existing bubble if any
        if person_id in self.bubbles:
            self.remove_bubble(person_id)
            
        # Create new bubble
        if self.use_pooling and self.bubble_pool:
            bubble = self.bubble_pool.acquire(person_id, position, text)
        else:
            bubble = Bubble(person_id, position, text)
            
        self.bubbles[person_id] = bubble
        self.logger.debug(f"Created bubble for person {person_id} at {position}")
        
        return bubble
        
    def update_bubble_position(self, person_id: str, position: Tuple[int, int]):
        """Update the position of a bubble."""
        if person_id in self.bubbles:
            self.bubbles[person_id].update(position)
            
    def remove_bubble(self, person_id: str):
        """Start fade animation for bubble removal."""
        if person_id in self.bubbles:
            self.bubbles[person_id].start_fade()
            self.logger.debug(f"Started fade for bubble {person_id}")
            
    def update(self):
        """Update all bubbles and remove invisible ones."""
        # Update all bubbles
        for bubble in list(self.bubbles.values()):
            bubble.update()
            
        # Remove invisible bubbles
        to_remove = [
            bubble_id for bubble_id, bubble in self.bubbles.items()
            if not bubble.is_visible
        ]
        for bubble_id in to_remove:
            bubble = self.bubbles.pop(bubble_id)
            
            # Return to pool if using pooling
            if self.use_pooling and self.bubble_pool:
                self.bubble_pool.release(bubble)
                
            self.logger.debug(f"Removed invisible bubble {bubble_id}")
            
    def draw(self, screen: pygame.Surface):
        """Draw all bubbles on the screen."""
        # Sort bubbles by Y position for proper layering
        sorted_bubbles = sorted(
            self.bubbles.values(),
            key=lambda b: b.current_position[1]
        )
        
        # Draw each bubble
        for bubble in sorted_bubbles:
            bubble.draw(screen)
            
    def handle_collisions(self):
        """Handle bubble collisions to prevent overlap."""
        bubbles_list = list(self.bubbles.values())
        
        for i in range(len(bubbles_list)):
            for j in range(i + 1, len(bubbles_list)):
                bubble1 = bubbles_list[i]
                bubble2 = bubbles_list[j]
                
                # Check collision
                rect1 = bubble1.get_bounds()
                rect2 = bubble2.get_bounds()
                
                if rect1.colliderect(rect2):
                    # Calculate push direction
                    dx = bubble1.current_position[0] - bubble2.current_position[0]
                    dy = bubble1.current_position[1] - bubble2.current_position[1]
                    
                    # Normalize
                    distance = max(1, (dx*dx + dy*dy)**0.5)
                    dx /= distance
                    dy /= distance
                    
                    # Push apart
                    push_force = 5
                    bubble1.current_position[0] += dx * push_force
                    bubble1.current_position[1] += dy * push_force
                    bubble2.current_position[0] -= dx * push_force
                    bubble2.current_position[1] -= dy * push_force
                    
    def get_bubble_count(self) -> int:
        """Get the current number of active bubbles."""
        return len(self.bubbles)
        
    def clear_all(self):
        """Start fade animation for all bubbles."""
        for bubble in self.bubbles.values():
            bubble.start_fade()
            
    def create_mock_bubbles(self, screen_size: Tuple[int, int], count: int = 3):
        """Create mock bubbles for testing."""
        width, height = screen_size
        
        for i in range(count):
            person_id = f"mock_person_{i}"
            # Random position in upper half of screen
            x = random.randint(100, width - 100)
            y = random.randint(100, height // 2)
            
            self.create_bubble(person_id, (x, y))
            
        self.logger.info(f"Created {count} mock bubbles for testing")