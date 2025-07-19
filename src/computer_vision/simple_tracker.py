"""Simple person tracker that maintains consistent IDs."""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging

from computer_vision.detector import Detection


@dataclass
class TrackedPerson:
    """A tracked person with persistent ID."""
    id: str
    last_position: Tuple[int, int]
    last_seen_frame: int
    assigned_thought_id: int  # Index of assigned thought
    

class SimpleTracker:
    """Simple tracker that maintains person IDs based on position."""
    
    def __init__(self, max_distance: float = 200.0, max_lost_frames: int = 30):
        self.logger = logging.getLogger(__name__)
        self.tracked_persons: Dict[str, TrackedPerson] = {}
        self.next_person_id = 0
        self.frame_count = 0
        self.max_distance = max_distance
        self.max_lost_frames = max_lost_frames
        
    def update(self, detections: List[Detection]) -> Dict[str, Tuple[Detection, int]]:
        """Update tracking and return dict of person_id -> (detection, thought_id)."""
        self.frame_count += 1
        matched = {}
        
        # First, try to match detections to existing tracks
        unmatched_detections = []
        used_tracks = set()
        
        for detection in detections:
            best_track_id = None
            best_distance = float('inf')
            
            # Find closest existing track
            for track_id, track in self.tracked_persons.items():
                if track_id in used_tracks:
                    continue
                    
                # Calculate distance
                dx = detection.head_position[0] - track.last_position[0]
                dy = detection.head_position[1] - track.last_position[1]
                distance = np.sqrt(dx*dx + dy*dy)
                
                if distance < self.max_distance and distance < best_distance:
                    best_distance = distance
                    best_track_id = track_id
            
            if best_track_id:
                # Match found - update existing track
                track = self.tracked_persons[best_track_id]
                track.last_position = detection.head_position
                track.last_seen_frame = self.frame_count
                used_tracks.add(best_track_id)
                matched[best_track_id] = (detection, track.assigned_thought_id)
                self.logger.debug(f"Matched detection to existing person {best_track_id}")
            else:
                # No match - will create new track
                unmatched_detections.append(detection)
        
        # Create new tracks for unmatched detections
        for detection in unmatched_detections:
            person_id = f"person_{self.next_person_id}"
            self.next_person_id += 1
            
            # Assign a consistent thought ID based on person ID
            thought_id = self.next_person_id % 50  # Assuming 50 thoughts
            
            track = TrackedPerson(
                id=person_id,
                last_position=detection.head_position,
                last_seen_frame=self.frame_count,
                assigned_thought_id=thought_id
            )
            
            self.tracked_persons[person_id] = track
            matched[person_id] = (detection, thought_id)
            self.logger.info(f"Created new track for person {person_id} with thought {thought_id}")
        
        # Remove old tracks
        tracks_to_remove = []
        for track_id, track in self.tracked_persons.items():
            if track_id not in matched:
                frames_lost = self.frame_count - track.last_seen_frame
                if frames_lost > self.max_lost_frames:
                    tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.tracked_persons[track_id]
            self.logger.info(f"Removed lost track {track_id}")
        
        return matched
    
    def reset(self):
        """Reset all tracking."""
        self.tracked_persons.clear()
        self.next_person_id = 0
        self.frame_count = 0