# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Thought Bubble Camera App - an interactive computer vision application that detects people through camera feed and displays animated thought bubbles above their heads with random text content.

## Development Commands

### Setup and Installation
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Run the main application
python src/main.py

# Run with debug mode
python src/main.py --debug

# Run tests
pytest tests/
```

### Development Tools
```bash
# Run linting
flake8 src/ tests/

# Format code
black src/ tests/

# Type checking
mypy src/
```

## Architecture Overview

The application follows a modular, event-driven architecture with these core components:

1. **Computer Vision Module** (`src/computer_vision/`)
   - Person detection using YOLO or MediaPipe
   - Face tracking and position calculation
   - Multi-person tracking with unique IDs

2. **Bubble System** (`src/bubble_system/`)
   - Bubble lifecycle management (creation, animation, destruction)
   - Physics-based movement and collision detection
   - Text rendering and formatting

3. **UI Layer** (`src/ui/`)
   - Camera feed display
   - Overlay rendering for bubbles
   - User controls and settings

4. **Main Application** (`src/main.py`)
   - Coordinates between vision, bubble system, and UI
   - Event loop management
   - Performance optimization (target: 30+ FPS)

## Key Technical Decisions

1. **Detection Framework**: Use MediaPipe for initial implementation (lighter weight), with option to switch to YOLO for better accuracy
2. **UI Framework**: Start with Tkinter for simplicity, consider PyQt6 for advanced features
3. **Threading**: Use separate threads for camera capture, detection, and UI rendering
4. **Thought Content**: Store in external `data/thoughts.txt` file for easy customization

## Important Implementation Notes

- The application processes video in real-time, requiring efficient frame processing
- Bubble positions are calculated relative to detected face coordinates with configurable offsets
- Each tracked person gets a unique ID to maintain bubble continuity
- Privacy: No data recording or storage - all processing is real-time only
- Performance target: Maintain 30+ FPS on modest hardware

## Testing Strategy

- Unit tests for individual components (detection, bubble physics, text management)
- Integration tests for component interactions
- Performance tests to ensure FPS targets
- UI tests for user interactions

## External Resources

The application requires:
- Webcam access for video input
- Pre-trained models (YOLO weights or MediaPipe models) in `data/models/`
- Custom thought content in `data/thoughts.txt`
- Font files in `assets/fonts/` for bubble text rendering