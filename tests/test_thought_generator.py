"""Unit tests for thought generator."""

import unittest
import tempfile
import os
from pathlib import Path

from src.bubble_system.thought_generator import ThoughtGenerator


class TestThoughtGenerator(unittest.TestCase):
    """Test cases for ThoughtGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary thoughts file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        self.temp_path = Path(self.temp_file.name)
        
        # Write test thoughts
        self.test_thoughts = [
            "First thought",
            "Second thought",
            "Third thought",
            "# This is a comment",
            "",  # Empty line
            "Fourth thought"
        ]
        self.temp_file.write('\n'.join(self.test_thoughts))
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_path)
        
    def test_load_thoughts_from_file(self):
        """Test loading thoughts from file."""
        generator = ThoughtGenerator(self.temp_path)
        
        # Should load non-empty, non-comment lines
        self.assertEqual(len(generator.thoughts), 4)
        self.assertIn("First thought", generator.thoughts)
        self.assertIn("Fourth thought", generator.thoughts)
        self.assertNotIn("# This is a comment", generator.thoughts)
        
    def test_load_with_missing_file(self):
        """Test loading with non-existent file."""
        generator = ThoughtGenerator(Path("nonexistent.txt"))
        
        # Should fall back to default thoughts
        self.assertGreater(len(generator.thoughts), 0)
        self.assertEqual(generator.thoughts, generator.default_thoughts)
        
    def test_get_random_thought(self):
        """Test getting random thoughts."""
        generator = ThoughtGenerator(self.temp_path)
        
        # Get multiple thoughts
        thoughts = [generator.get_random_thought() for _ in range(20)]
        
        # All should be valid thoughts
        for thought in thoughts:
            self.assertIn(thought, generator.thoughts)
            
        # Should have some variety (not all the same)
        unique_thoughts = set(thoughts)
        self.assertGreater(len(unique_thoughts), 1)
        
    def test_add_remove_thoughts(self):
        """Test runtime thought management."""
        generator = ThoughtGenerator(self.temp_path)
        initial_count = generator.get_thought_count()
        
        # Add new thought
        new_thought = "New runtime thought"
        generator.add_thought(new_thought)
        self.assertEqual(generator.get_thought_count(), initial_count + 1)
        self.assertIn(new_thought, generator.thoughts)
        
        # Remove thought
        generator.remove_thought("First thought")
        self.assertEqual(generator.get_thought_count(), initial_count)
        self.assertNotIn("First thought", generator.thoughts)
        
    def test_reload_thoughts(self):
        """Test hot reload functionality."""
        generator = ThoughtGenerator(self.temp_path)
        initial_count = generator.get_thought_count()
        
        # Modify file
        with open(self.temp_path, 'a') as f:
            f.write("\nNew hot-loaded thought")
            
        # Reload
        generator.reload_thoughts()
        
        # Should have new thought
        self.assertEqual(generator.get_thought_count(), initial_count + 1)
        self.assertIn("New hot-loaded thought", generator.thoughts)
        
    def test_validate_thought_length(self):
        """Test thought length validation."""
        generator = ThoughtGenerator()
        
        # Valid length
        self.assertTrue(generator.validate_thought_length("Normal thought"))
        
        # Too short
        self.assertFalse(generator.validate_thought_length(""))
        
        # Too long
        long_thought = "x" * 150
        self.assertFalse(generator.validate_thought_length(long_thought))


if __name__ == '__main__':
    unittest.main()