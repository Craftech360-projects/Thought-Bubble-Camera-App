"""Build script for creating standalone executable."""

import subprocess
import sys
import shutil
from pathlib import Path
import platform


def clean_build_dirs():
    """Clean previous build artifacts."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"Cleaning {dir_name}/...")
            shutil.rmtree(dir_path)
            
    # Clean .pyc files
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink()
        
    # Clean .pyo files
    for pyo_file in Path('.').rglob('*.pyo'):
        pyo_file.unlink()
        

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print(f"PyInstaller {PyInstaller.__version__} is installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller==6.1.0'])
        

def build_executable():
    """Build the executable using PyInstaller."""
    print("\nBuilding executable...")
    
    # Base PyInstaller command
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        'thought_bubble_app.spec',
        '--clean',
        '--noconfirm'
    ]
    
    # Run PyInstaller
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
        
    print("Build completed successfully!")
    return True
    

def create_distribution():
    """Create distribution package with all necessary files."""
    print("\nCreating distribution package...")
    
    dist_dir = Path('dist')
    
    # Copy additional files that might be needed
    files_to_copy = [
        'README.md',
        'SETUP_INSTRUCTIONS.md',
        'requirements.txt'
    ]
    
    for file_name in files_to_copy:
        src = Path(file_name)
        if src.exists():
            dst = dist_dir / file_name
            shutil.copy2(src, dst)
            print(f"Copied {file_name}")
            
    # Create a sample thoughts file if it doesn't exist in dist
    thoughts_dir = dist_dir / 'data' / 'thoughts'
    if not thoughts_dir.exists():
        thoughts_dir.mkdir(parents=True, exist_ok=True)
        
    thoughts_file = thoughts_dir / 'thoughts.txt'
    if not thoughts_file.exists():
        shutil.copy2('data/thoughts/thoughts.txt', thoughts_file)
        print("Copied thoughts.txt")
        
    print("Distribution package created!")
    

def create_dmg_installer():
    """Create a .dmg installer for macOS."""
    if platform.system() != 'Darwin':
        print("\nSkipping .dmg creation (not on macOS).")
        return

    print("\nCreating .dmg installer...")
    
    # Check for create-dmg tool
    if not shutil.which('create-dmg'):
        print("Error: 'create-dmg' command not found.")
        print("Please install it using Homebrew: brew install create-dmg")
        return False

    dist_dir = Path('dist')
    app_name = 'ThoughtBubbleCamera'
    app_path = dist_dir / f"{app_name}.app"
    dmg_path = dist_dir / f"{app_name}.dmg"

    if not app_path.exists():
        print(f"Error: {app_path} not found. Run the build first.")
        return False

    # Command to create DMG
    cmd = [
        'create-dmg',
        '--volname', f'{app_name} Installer',
        '--window-pos', '200', '120',
        '--window-size', '800', '400',
        '--icon-size', '100',
        '--app-drop-link', '600', '185',
        str(dmg_path),
        str(app_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("DMG creation failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    print(f"Successfully created {dmg_path}")
    return True


def main():
    """Main build process."""
    print("Thought Bubble Camera App - Build Script")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    print("-" * 50)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build executable
    if build_executable():
        # Create distribution
        create_distribution()

        # Create DMG installer for macOS
        if platform.system() == 'Darwin':
            create_dmg_installer()
        
        print("\n" + "=" * 50)
        print("BUILD SUCCESSFUL!")
        print("=" * 50)
        
        # Show output location
        dist_dir = Path('dist')
        if platform.system() == 'Darwin':
            app_path = dist_dir / 'ThoughtBubbleCamera.app'
            if app_path.exists():
                print(f"\nApplication bundle created at: {app_path}")
                print("\nTo run the app:")
                print(f"  open {app_path}")
        else:
            exe_name = 'ThoughtBubbleCamera.exe' if platform.system() == 'Windows' else 'ThoughtBubbleCamera'
            exe_path = dist_dir / exe_name
            if exe_path.exists():
                print(f"\nExecutable created at: {exe_path}")
                print("\nTo run the app:")
                print(f"  ./{exe_path}")
    else:
        print("\n" + "=" * 50)
        print("BUILD FAILED!")
        print("=" * 50)
        sys.exit(1)
        

if __name__ == '__main__':
    main()