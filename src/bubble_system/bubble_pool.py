"""Object pooling for bubble instances to improve performance."""

import logging
from typing import List, Optional, Tuple
from collections import deque

from bubble_system.bubble import Bubble
from bubble_system.bubble_styles import get_style_for_person


class BubblePool:
    """Pool of reusable bubble objects to reduce allocation overhead."""
    
    def __init__(self, initial_size: int = 10, max_size: int = 50):
        self.logger = logging.getLogger(__name__)
        self.initial_size = initial_size
        self.max_size = max_size
        
        # Available bubbles for reuse
        self.available_bubbles: deque[Bubble] = deque()
        
        # Active bubbles currently in use
        self.active_bubbles: List[Bubble] = []
        
        # Total bubbles created
        self.total_created = 0
        
        # Pre-create initial pool
        self._initialize_pool()
        
    def _initialize_pool(self):
        """Create initial pool of bubbles."""
        for i in range(self.initial_size):
            bubble = self._create_bubble(f"pool_{i}", (0, 0), "...")
            bubble.is_visible = False
            self.available_bubbles.append(bubble)
            
        self.logger.info(f"Initialized bubble pool with {self.initial_size} bubbles")
        
    def _create_bubble(self, bubble_id: str, position: Tuple[int, int], text: str) -> Bubble:
        """Create a new bubble instance."""
        self.total_created += 1
        return Bubble(bubble_id, position, text)
        
    def acquire(self, bubble_id: str, position: Tuple[int, int], text: str) -> Bubble:
        """Get a bubble from the pool or create a new one."""
        bubble = None
        
        # Try to get from pool
        if self.available_bubbles:
            bubble = self.available_bubbles.popleft()
            # Reinitialize the bubble
            self._reinitialize_bubble(bubble, bubble_id, position, text)
            self.logger.debug(f"Reused bubble from pool for {bubble_id}")
        else:
            # Create new bubble if under max size
            if self.total_created < self.max_size:
                bubble = self._create_bubble(bubble_id, position, text)
                self.logger.debug(f"Created new bubble for {bubble_id}")
            else:
                # Pool exhausted, reuse oldest active bubble
                if self.active_bubbles:
                    bubble = self.active_bubbles.pop(0)
                    self._reinitialize_bubble(bubble, bubble_id, position, text)
                    self.logger.warning(f"Pool exhausted, recycled oldest bubble for {bubble_id}")
                    
        if bubble:
            self.active_bubbles.append(bubble)
            
        return bubble
        
    def release(self, bubble: Bubble):
        """Return a bubble to the pool."""
        if bubble in self.active_bubbles:
            self.active_bubbles.remove(bubble)
            
        # Reset bubble state
        bubble.is_visible = False
        bubble.fade_start_time = None
        
        # Add back to pool if not at capacity
        if len(self.available_bubbles) < self.max_size:
            self.available_bubbles.append(bubble)
            self.logger.debug(f"Released bubble {bubble.id} back to pool")
        else:
            self.logger.debug(f"Pool at capacity, discarding bubble {bubble.id}")
            
    def _reinitialize_bubble(self, bubble: Bubble, bubble_id: str, position: Tuple[int, int], text: str):
        """Reinitialize a pooled bubble with new data."""
        import time
        
        # Update basic properties
        bubble.id = bubble_id
        bubble.base_position = position
        bubble.current_position = list(position)
        bubble.text = text
        
        # Reset animation state
        bubble.creation_time = time.time()
        bubble.is_visible = True
        bubble.fade_start_time = None
        bubble.sway_offset = 0
        bubble.bounce_offset = 0
        bubble.bounce_velocity = 0
        
        # Update style based on new ID
        bubble.style_variant = get_style_for_person(bubble_id)
        
        # Recalculate size and re-render
        bubble._calculate_size()
        bubble._render_bubble_surface()
        
    def clear_all(self):
        """Clear all active bubbles and return them to pool."""
        while self.active_bubbles:
            bubble = self.active_bubbles.pop()
            self.release(bubble)
            
    def get_stats(self) -> dict:
        """Get pool statistics."""
        return {
            "active": len(self.active_bubbles),
            "available": len(self.available_bubbles),
            "total_created": self.total_created,
            "pool_efficiency": len(self.available_bubbles) / max(1, self.total_created)
        }