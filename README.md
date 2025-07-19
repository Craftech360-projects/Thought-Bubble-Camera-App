# Thought Bubble Camera App

An interactive computer vision application that detects people through camera feed and displays animated thought bubbles above their heads with random thoughts.

## Features
- ✅ **Real-time person detection** using MediaPipe
- ✅ **Multi-person tracking** with unique ID persistence
- ✅ **Animated thought bubbles** with 7 style variations
- ✅ **Smooth animations** including sway, bounce, and fade effects
- ✅ **Customizable settings** via interactive panel
- ✅ **Performance optimizations** with multi-threading and object pooling
- ✅ **50+ custom thoughts** loaded from external file

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Webcam (built-in or USB)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd Chat-Bubble-App

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application
```bash
python src/main.py
```

## Usage

### Controls
- **Start/Stop Camera**: Toggle camera feed and person detection
- **Show/Hide Bubbles**: Toggle thought bubble display
- **Debug**: Show detection boxes and tracking info
- **Settings**: Expand panel to customize appearance
- **F11**: Toggle fullscreen mode
- **Escape**: Exit fullscreen

### Settings Panel
- **Bubble Color**: Choose bubble background color
- **Text Color**: Choose text color
- **Font Size**: Adjust text size (12-24pt)
- **Transparency**: Adjust bubble opacity
- **Sway Amount**: Control bubble swaying motion
- **Animation Speed**: Adjust overall animation speed
- **Show Shadows**: Toggle bubble shadows

### Customizing Thoughts
Edit `data/thoughts/thoughts.txt` to add your own custom thoughts. Each line is a separate thought that can appear in bubbles.

## Architecture

### Core Components
1. **Computer Vision** (`src/computer_vision/`)
   - `camera_handler.py`: Multi-threaded camera capture
   - `detector.py`: Person detection using MediaPipe Pose/Face
   - `tracker.py`: Multi-person tracking with ID persistence

2. **Bubble System** (`src/bubble_system/`)
   - `bubble.py`: Individual bubble with animations
   - `bubble_renderer.py`: Manages multiple bubbles
   - `bubble_styles.py`: 7 predefined style variations
   - `thought_generator.py`: Loads and manages thought content
   - `bubble_pool.py`: Object pooling for performance

3. **User Interface** (`src/ui/`)
   - `main_window.py`: Tkinter window with embedded Pygame
   - `overlay_renderer.py`: Combines camera feed with bubbles
   - `settings_panel.py`: Interactive settings controls

### Performance Features
- **Multi-threading**: Separate threads for camera, detection, and UI
- **Frame skipping**: Adaptive detection frequency based on performance
- **Object pooling**: Reuses bubble instances to reduce memory allocation
- **Position interpolation**: Smooth bubble movement between detections

## Building Standalone Executable

```bash
# Install PyInstaller (if not already installed)
pip install pyinstaller==6.1.0

# Run build script
python build.py
```

The executable will be created in the `dist/` directory:
- **Windows**: `dist/ThoughtBubbleCamera.exe`
- **macOS**: `dist/ThoughtBubbleCamera.app`
- **Linux**: `dist/ThoughtBubbleCamera`

## Testing

Run unit tests:
```bash
python -m pytest tests/
```

## Troubleshooting

### Camera Not Working
- Ensure your camera is connected and not being used by another application
- Check camera permissions in your system settings
- The app will fall back to mock camera mode if real camera fails

### Low Performance
- Reduce the number of tracked people in view
- Lower the camera resolution in settings
- Close other resource-intensive applications

### Dependencies Issues
- Ensure you're using Python 3.8 or higher
- Try reinstalling dependencies: `pip install -r requirements.txt --force-reinstall`
- On macOS, you may need to install additional system dependencies for OpenCV

## License
This project is provided as-is for educational and entertainment purposes.