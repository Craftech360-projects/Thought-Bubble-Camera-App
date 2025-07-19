"""Unit tests for bubble system."""

import unittest
import pygame
from unittest.mock import Mock, patch

# Initialize pygame for tests
pygame.init()

from src.bubble_system.bubble import Bubble
from src.bubble_system.bubble_styles import get_random_style


class TestBubble(unittest.TestCase):
    """Test cases for Bubble class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.bubble_id = "test_bubble_1"
        self.position = (100, 200)
        self.text = "Test thought"
        
    def test_bubble_creation(self):
        """Test bubble creation with basic parameters."""
        bubble = Bubble(self.bubble_id, self.position, self.text)
        
        self.assertEqual(bubble.id, self.bubble_id)
        self.assertEqual(bubble.base_position, self.position)
        self.assertEqual(bubble.text, self.text)
        self.assertTrue(bubble.is_visible)
        self.assertIsNone(bubble.fade_start_time)
        
    def test_bubble_size_calculation(self):
        """Test bubble size calculation based on text."""
        # Short text
        short_bubble = Bubble("b1", (0, 0), "Hi")
        
        # Long text
        long_text = "This is a very long thought that should wrap to multiple lines"
        long_bubble = Bubble("b2", (0, 0), long_text)
        
        # Long bubble should be larger
        self.assertGreater(long_bubble.width, short_bubble.width)
        self.assertGreater(long_bubble.height, short_bubble.height)
        
    def test_bubble_update_position(self):
        """Test bubble position update and interpolation."""
        bubble = Bubble(self.bubble_id, self.position, self.text)
        
        # Update to new position
        new_position = (200, 300)
        bubble.update(new_position)
        
        # Position should start moving towards target
        self.assertNotEqual(bubble.current_position, list(self.position))
        
        # After multiple updates, should get closer to target
        for _ in range(10):
            bubble.update()
            
        # Should be very close to target
        self.assertAlmostEqual(bubble.current_position[0], new_position[0], delta=10)
        self.assertAlmostEqual(bubble.current_position[1], new_position[1], delta=10)
        
    def test_bubble_fade(self):
        """Test bubble fade animation."""
        bubble = Bubble(self.bubble_id, self.position, self.text)
        
        # Initial alpha should be increasing (fade in)
        initial_alpha = bubble.get_alpha()
        self.assertLessEqual(initial_alpha, 255)
        
        # Start fade out
        bubble.start_fade()
        self.assertIsNotNone(bubble.fade_start_time)
        
        # Alpha should decrease during fade out
        with patch('time.time', return_value=bubble.fade_start_time + 0.5):
            fade_alpha = bubble.get_alpha()
            self.assertLess(fade_alpha, initial_alpha)
            
    def test_bubble_bounds(self):
        """Test bubble bounding rectangle calculation."""
        bubble = Bubble(self.bubble_id, self.position, self.text)
        bounds = bubble.get_bounds()
        
        self.assertIsInstance(bounds, pygame.Rect)
        self.assertGreater(bounds.width, 0)
        self.assertGreater(bounds.height, 0)
        
    def test_bubble_style_variants(self):
        """Test bubble creation with different styles."""
        style = get_random_style()
        bubble = Bubble(self.bubble_id, self.position, self.text, style)
        
        self.assertEqual(bubble.style_variant, style)
        self.assertEqual(bubble.style.fill_color, style.fill_color)
        self.assertEqual(bubble.style.border_color, style.border_color)


if __name__ == '__main__':
    unittest.main()