"""Configuration management for Thought Bubble App."""

import os
from pathlib import Path

# Application settings
APP_NAME = "Thought Bubble Camera"
VERSION = "0.1.0"

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# Camera settings
CAMERA_FPS = 30
CAMERA_DEFAULT_INDEX = 0

# Bubble settings
BUBBLE_MIN_SIZE = (150, 80)
BUBBLE_MAX_SIZE = (300, 150)
BUBBLE_PADDING = 20
BUBBLE_TAIL_HEIGHT = 20
BUBBLE_OFFSET_Y = 50  # Pixels above head
BUBBLE_FADE_DURATION = 0.5  # seconds
BUBBLE_SWAY_AMPLITUDE = 5  # pixels
BUBBLE_SWAY_SPEED = 2  # oscillations per second

# Text settings
DEFAULT_FONT_SIZE = 16
MIN_FONT_SIZE = 12
MAX_FONT_SIZE = 24
TEXT_COLOR = (0, 0, 0)  # Black
BUBBLE_COLOR = (255, 255, 255)  # White
BUBBLE_ALPHA = 230  # 0-255 transparency

# Performance settings
FRAME_SKIP = 2  # Process every Nth frame for detection
MAX_TRACKED_PERSONS = 10
INTERPOLATION_SMOOTHING = 0.3

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
FONTS_DIR = ASSETS_DIR / "fonts"
THOUGHTS_FILE = DATA_DIR / "thoughts" / "thoughts.txt"

# UI Colors
UI_BACKGROUND = (30, 30, 30)
UI_BUTTON_PRIMARY = (70, 130, 220)
UI_BUTTON_HOVER = (80, 140, 230)
UI_BUTTON_ACTIVE = (60, 120, 210)
UI_TEXT_PRIMARY = (255, 255, 255)
UI_STATUS_GREEN = (50, 205, 50)
UI_STATUS_RED = (220, 50, 50)