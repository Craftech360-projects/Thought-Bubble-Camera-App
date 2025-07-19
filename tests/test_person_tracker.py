"""Unit tests for person tracker."""

import unittest
from src.computer_vision.detector import Detection
from src.computer_vision.tracker import PersonTracker, TrackedPerson


class TestPersonTracker(unittest.TestCase):
    """Test cases for PersonTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = PersonTracker(max_lost_frames=5)
        
    def test_new_person_tracking(self):
        """Test tracking a new person."""
        # Create detection
        detection = Detection(
            id="det_1",
            bbox=(100, 100, 50, 100),
            head_position=(125, 100),
            confidence=0.9
        )
        
        # Update tracker
        results = self.tracker.update([detection])
        
        # Should create new track
        self.assertEqual(len(results), 1)
        person_id, tracked_det = results[0]
        self.assertTrue(person_id.startswith("person_"))
        self.assertEqual(tracked_det, detection)
        
        # Check tracked person
        self.assertEqual(len(self.tracker.tracked_persons), 1)
        tracked = self.tracker.tracked_persons[person_id]
        self.assertTrue(tracked.active)
        self.assertEqual(tracked.last_detection, detection)
        
    def test_person_reidentification(self):
        """Test maintaining person ID across frames."""
        # First frame
        det1 = Detection("d1", (100, 100, 50, 100), (125, 100), 0.9)
        results1 = self.tracker.update([det1])
        person_id = results1[0][0]
        
        # Second frame - slightly moved
        det2 = Detection("d2", (110, 105, 50, 100), (135, 105), 0.9)
        results2 = self.tracker.update([det2])
        
        # Should maintain same ID
        self.assertEqual(len(results2), 1)
        self.assertEqual(results2[0][0], person_id)
        
    def test_multiple_people_tracking(self):
        """Test tracking multiple people."""
        # Create multiple detections
        detections = [
            Detection("d1", (100, 100, 50, 100), (125, 100), 0.9),
            Detection("d2", (300, 100, 50, 100), (325, 100), 0.8),
            Detection("d3", (500, 100, 50, 100), (525, 100), 0.7)
        ]
        
        # Update tracker
        results = self.tracker.update(detections)
        
        # Should track all three
        self.assertEqual(len(results), 3)
        self.assertEqual(len(self.tracker.tracked_persons), 3)
        
        # All should be active
        for person in self.tracker.tracked_persons.values():
            self.assertTrue(person.active)
            
    def test_lost_person_removal(self):
        """Test removal of lost tracks."""
        # Track a person
        det1 = Detection("d1", (100, 100, 50, 100), (125, 100), 0.9)
        results1 = self.tracker.update([det1])
        person_id = results1[0][0]
        
        # Update without detection for several frames
        for _ in range(self.tracker.max_lost_frames + 1):
            self.tracker.update([])
            
        # Person should be removed
        self.assertNotIn(person_id, self.tracker.tracked_persons)
        
    def test_position_interpolation(self):
        """Test position smoothing."""
        # Create person with movement
        positions = [(100, 100), (110, 105), (120, 110), (130, 115), (140, 120)]
        
        person_id = None
        for i, pos in enumerate(positions):
            det = Detection(f"d{i}", (pos[0]-25, pos[1], 50, 100), pos, 0.9)
            results = self.tracker.update([det])
            if person_id is None:
                person_id = results[0][0]
                
        # Get interpolated position
        interp_pos = self.tracker.get_interpolated_position(person_id)
        self.assertIsNotNone(interp_pos)
        
        # Should be smoothed (not exactly the last position)
        self.assertNotEqual(interp_pos, positions[-1])
        
    def test_tracker_reset(self):
        """Test tracker reset functionality."""
        # Add some tracks
        detections = [
            Detection("d1", (100, 100, 50, 100), (125, 100), 0.9),
            Detection("d2", (300, 100, 50, 100), (325, 100), 0.8)
        ]
        self.tracker.update(detections)
        
        # Reset
        self.tracker.reset()
        
        # Should be empty
        self.assertEqual(len(self.tracker.tracked_persons), 0)
        self.assertEqual(self.tracker.next_id, 0)
        self.assertEqual(self.tracker.frame_count, 0)


if __name__ == '__main__':
    unittest.main()