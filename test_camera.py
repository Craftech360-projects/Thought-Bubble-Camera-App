"""Test camera access on macOS."""

import cv2
import sys

def test_camera():
    """Test if camera can be accessed."""
    print("Testing camera access...")
    
    # Try different camera indices
    for index in [0, 1, 2]:
        print(f"\nTrying camera index {index}...")
        cap = cv2.VideoCapture(index)
        
        if cap.isOpened():
            print(f"✓ Camera {index} opened successfully!")
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✓ Successfully read frame: {frame.shape}")
                cap.release()
                return True
            else:
                print(f"✗ Failed to read frame from camera {index}")
                cap.release()
        else:
            print(f"✗ Failed to open camera {index}")
    
    print("\nNo working camera found!")
    print("\nTroubleshooting tips:")
    print("1. Check System Preferences > Security & Privacy > Privacy > Camera")
    print("2. Make sure Python/Terminal has camera access permission")
    print("3. Try running: tccutil reset Camera")
    
    return False

if __name__ == "__main__":
    if test_camera():
        print("\nCamera test passed! ✓")
    else:
        print("\nCamera test failed! ✗")
        sys.exit(1)