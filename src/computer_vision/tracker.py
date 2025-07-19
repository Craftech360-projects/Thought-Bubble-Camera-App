"""Multi-person tracking to maintain consistent IDs."""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

from computer_vision.detector import Detection


@dataclass
class TrackedPerson:
    """Represents a tracked person with history."""
    id: str
    last_detection: Detection
    last_seen_frame: int
    history: List[Tuple[int, int]]  # History of positions
    active: bool = True
    

class PersonTracker:
    """Tracks multiple people across frames to maintain consistent IDs."""
    
    def __init__(self, max_lost_frames: int = 30):
        self.logger = logging.getLogger(__name__)
        self.tracked_persons: Dict[str, TrackedPerson] = {}
        self.next_id = 0
        self.frame_count = 0
        self.max_lost_frames = max_lost_frames
        
    def update(self, detections: List[Detection]) -> List[Tuple[str, Detection]]:
        """Update tracking with new detections, returns list of (person_id, detection)."""
        self.frame_count += 1
        matched_detections = []
        
        # Mark all existing tracks as potentially lost
        for person in self.tracked_persons.values():
            person.active = False
            
        # Match detections to existing tracks
        unmatched_detections = []
        for detection in detections:
            matched_id = self._find_match(detection)
            
            if matched_id:
                # Update existing track
                person = self.tracked_persons[matched_id]
                person.last_detection = detection
                person.last_seen_frame = self.frame_count
                person.active = True
                person.history.append(detection.head_position)
                
                # Keep history limited
                if len(person.history) > 30:
                    person.history.pop(0)
                    
                matched_detections.append((matched_id, detection))
            else:
                unmatched_detections.append(detection)
                
        # Create new tracks for unmatched detections
        for detection in unmatched_detections:
            new_id = f"person_{self.next_id}"
            self.next_id += 1
            
            self.tracked_persons[new_id] = TrackedPerson(
                id=new_id,
                last_detection=detection,
                last_seen_frame=self.frame_count,
                history=[detection.head_position],
                active=True
            )
            
            matched_detections.append((new_id, detection))
            self.logger.debug(f"New person tracked: {new_id}")
            
        # Remove tracks that have been lost for too long
        lost_ids = []
        for person_id, person in self.tracked_persons.items():
            if not person.active:
                frames_lost = self.frame_count - person.last_seen_frame
                if frames_lost > self.max_lost_frames:
                    lost_ids.append(person_id)
                    
        for person_id in lost_ids:
            del self.tracked_persons[person_id]
            self.logger.debug(f"Lost track of person: {person_id}")
            
        return matched_detections
        
    def _find_match(self, detection: Detection) -> Optional[str]:
        """Find the best matching tracked person for a detection."""
        best_match_id = None
        best_distance = float('inf')
        
        # Use simple distance-based matching
        for person_id, person in self.tracked_persons.items():
            if person.active:
                continue
                
            # Calculate distance between head positions
            last_pos = person.last_detection.head_position
            curr_pos = detection.head_position
            
            distance = np.sqrt(
                (last_pos[0] - curr_pos[0]) ** 2 + 
                (last_pos[1] - curr_pos[1]) ** 2
            )
            
            # Consider match if within threshold
            if distance < 100 and distance < best_distance:
                best_match_id = person_id
                best_distance = distance
                
        return best_match_id
        
    def get_active_persons(self) -> List[TrackedPerson]:
        """Get list of currently active tracked persons."""
        return [p for p in self.tracked_persons.values() if p.active]
        
    def get_interpolated_position(self, person_id: str) -> Optional[Tuple[int, int]]:
        """Get smoothed position for a person based on history."""
        if person_id not in self.tracked_persons:
            return None
            
        person = self.tracked_persons[person_id]
        if not person.history:
            return None
            
        # Simple moving average over recent positions
        recent_positions = person.history[-5:]
        if recent_positions:
            avg_x = int(sum(p[0] for p in recent_positions) / len(recent_positions))
            avg_y = int(sum(p[1] for p in recent_positions) / len(recent_positions))
            return (avg_x, avg_y)
            
        return person.last_detection.head_position
        
    def reset(self):
        """Reset all tracking."""
        self.tracked_persons.clear()
        self.next_id = 0
        self.frame_count = 0
        self.logger.info("Tracker reset")