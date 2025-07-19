"""Thought generator that loads and manages thought content."""

import random
import logging
from pathlib import Path
from typing import List, Optional

from utils.config import THOUGHTS_FILE


class ThoughtGenerator:
    """Manages loading and selection of thought texts."""
    
    def __init__(self, thoughts_file: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.thoughts_file = thoughts_file or THOUGHTS_FILE
        self.thoughts: List[str] = []
        
        # Default thoughts as fallback
        self.default_thoughts = [
            "I wonder what's for lunch...",
            "Did I leave the stove on?",
            "This is so cool!",
            "Is it Friday yet?",
            "I should call my mom.",
            "What was I thinking about?",
            "Coffee sounds good right now.",
            "I love this song!",
            "Time for a break.",
            "Almost done with work!",
        ]
        
        # Load thoughts on initialization
        self.load_thoughts()
        
    def load_thoughts(self) -> bool:
        """Load thoughts from file."""
        try:
            if self.thoughts_file.exists():
                with open(self.thoughts_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # Clean and filter thoughts
                self.thoughts = [
                    line.strip() 
                    for line in lines 
                    if line.strip() and not line.startswith('#')
                ]
                
                if self.thoughts:
                    self.logger.info(f"Loaded {len(self.thoughts)} thoughts from {self.thoughts_file}")
                    return True
                else:
                    self.logger.warning("No valid thoughts found in file, using defaults")
                    self.thoughts = self.default_thoughts.copy()
            else:
                self.logger.warning(f"Thoughts file not found: {self.thoughts_file}, using defaults")
                self.thoughts = self.default_thoughts.copy()
                
        except Exception as e:
            self.logger.error(f"Error loading thoughts: {e}")
            self.thoughts = self.default_thoughts.copy()
            
        return False
        
    def get_random_thought(self) -> str:
        """Get a random thought from the pool."""
        if not self.thoughts:
            return "..."  # Fallback if somehow no thoughts available
            
        return random.choice(self.thoughts)
        
    def reload_thoughts(self):
        """Reload thoughts from file (hot reload)."""
        old_count = len(self.thoughts)
        self.load_thoughts()
        new_count = len(self.thoughts)
        
        if old_count != new_count:
            self.logger.info(f"Thoughts reloaded: {old_count} -> {new_count}")
            
    def add_thought(self, thought: str):
        """Add a new thought to the pool (runtime only)."""
        if thought and thought not in self.thoughts:
            self.thoughts.append(thought)
            self.logger.debug(f"Added new thought: {thought}")
            
    def remove_thought(self, thought: str):
        """Remove a thought from the pool (runtime only)."""
        if thought in self.thoughts and len(self.thoughts) > 1:
            self.thoughts.remove(thought)
            self.logger.debug(f"Removed thought: {thought}")
            
    def get_thought_count(self) -> int:
        """Get the current number of thoughts."""
        return len(self.thoughts)
        
    def validate_thought_length(self, thought: str, max_length: int = 100) -> bool:
        """Check if a thought is within acceptable length."""
        return 0 < len(thought) <= max_length