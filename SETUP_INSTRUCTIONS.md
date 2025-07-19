# Setup Instructions for Thought Bubble Camera App

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Setup Steps

1. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on macOS/Linux:
   source venv/bin/activate
   
   # Activate on Windows:
   venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python src/main.py
   ```

## Usage

### Main Controls
- **Start Camera**: Click to start the mock camera feed
- **Show Bubbles**: Click to enable thought bubbles
- **F11**: Toggle fullscreen mode
- **Escape**: Exit fullscreen mode

### Settings Panel
- Click the "◀ Settings" button on the right to expand the settings panel
- Adjust bubble appearance, colors, and animations
- Changes apply in real-time

### Current Features
- ✅ UI framework with Tkinter + Pygame
- ✅ Mock camera feed display
- ✅ Animated thought bubbles
- ✅ Settings panel for customization
- ✅ Thought content loading from file
- ✅ 30 FPS rendering loop

### Features In Development
- ⏳ Real camera integration
- ⏳ Computer vision person detection
- ⏳ Multi-person tracking
- ⏳ Performance optimizations
- ⏳ Advanced animations

## Customizing Thoughts
Edit the file `data/thoughts/thoughts.txt` to add your own custom thoughts. Each line is a separate thought that can appear in bubbles.

## Troubleshooting
- If Pygame embedding fails, the app will fall back to a Tkinter canvas
- Check the console for error messages
- Ensure all dependencies are installed correctly