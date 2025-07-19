"""Main application window using Tkinter with embedded Pygame."""

import tkinter as tk
from tkinter import ttk
import pygame
import logging
import os
import sys
from typing import Optional

from utils.config import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT,
    UI_BACKGROUND, CAMERA_FPS, BUBBLE_OFFSET_Y
)
from bubble_system.bubble_renderer import BubbleRenderer
# from ui.settings_panel import SettingsPanel  # Commented out for simplified UI
from ui.overlay_renderer import OverlayRenderer


class MainWindow:
    """Main application window with Tkinter frame and embedded Pygame."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Set environment variable to suppress Tk deprecation warning
        os.environ['TK_SILENCE_DEPRECATION'] = '1'
        
        self.root = tk.Tk()
        self.running = False
        self.is_fullscreen = False
        self.camera_active = False
        self.fps_clock = pygame.time.Clock()
        self.current_fps = 0
        
        # Initialize Pygame before embedding
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        os.environ['SDL_VIDEO_ALLOW_SCREENSAVER'] = '1'
        
        # Initialize Pygame with specific video driver for macOS
        if sys.platform == 'darwin':
            # Use a different approach for macOS
            try:
                pygame.display.init()
                pygame.font.init()
            except pygame.error as e:
                self.logger.warning(f"Pygame init warning: {e}")
        else:
            pygame.init()
        
        # Initialize renderers
        self.bubble_renderer = BubbleRenderer()
        self.overlay_renderer = None
        self.show_bubbles = False
        self.use_real_camera = True  # Use real camera by default
        self.use_embedded_pygame = False  # Flag to control embedding
        self.pygame_fullscreen = False  # Track Pygame window fullscreen state
        
        # Setup window
        self._setup_window()
        self._setup_ui()
        
    def _setup_window(self):
        """Configure the main window."""
        self.root.title(APP_NAME)
        # Make control window smaller and more focused
        control_width = 600
        control_height = 200
        self.root.geometry(f"{control_width}x{control_height}")
        self.root.minsize(control_width, control_height)
        self.root.maxsize(control_width, control_height)  # Fixed size
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (WINDOW_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (WINDOW_HEIGHT // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        
        # Configure window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Bind keyboard shortcuts
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen())
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
    def _setup_ui(self):
        """Setup the UI components."""
        # Main container
        self.main_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = tk.Label(
            self.main_frame,
            text="Thought Bubble Camera Controls",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(10, 5))
        
        # Control panel in center
        self.control_panel = tk.Frame(self.main_frame, bg='#2b2b2b')
        self.control_panel.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Add controls
        self._create_controls()
        
        # Don't create settings panel for simplified UI
        # self.settings_panel = SettingsPanel(
        #     self.main_frame,
        #     on_settings_change=self._on_settings_change
        # )
        
        # For macOS, create a separate Pygame window instead of embedding
        if sys.platform == 'darwin':
            self._create_separate_pygame_window()
        else:
            # Embed Pygame surface
            self.camera_frame.update()
            self._embed_pygame()
        
    def _create_separate_pygame_window(self):
        """Create a separate Pygame window for macOS."""
        try:
            # Get Tkinter window position
            self.root.update_idletasks()
            tk_x = self.root.winfo_x()
            tk_y = self.root.winfo_y()
            
            # Position Pygame window next to Tkinter window
            os.environ['SDL_VIDEO_WINDOW_POS'] = f'{tk_x + WINDOW_WIDTH + 20},{tk_y}'
            
            # Create Pygame display
            self.pygame_width = 1024
            self.pygame_height = 768
            self.screen = pygame.display.set_mode((self.pygame_width, self.pygame_height))
            pygame.display.set_caption(f"{APP_NAME} - Camera View")
            
            # Initialize overlay renderer with screen
            self.overlay_renderer = OverlayRenderer(self.screen)
            
            self.logger.info("Created separate Pygame window for macOS")
            
            # No need for instruction label in control window
            
        except pygame.error as e:
            self.logger.error(f"Failed to create Pygame window: {e}")
            self._create_fallback_canvas()
            
    def _embed_pygame(self):
        """Embed Pygame surface in Tkinter frame."""
        # Get the window handle
        os.environ['SDL_WINDOWID'] = str(self.camera_frame.winfo_id())
        
        # On Windows, we need to set SDL_VIDEODRIVER
        if sys.platform == "win32":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        
        # Create Pygame display
        self.camera_frame.update()
        width = self.camera_frame.winfo_width()
        height = self.camera_frame.winfo_height()
        
        try:
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.init()
            self.logger.info(f"Pygame surface created: {width}x{height}")
            
            # Initialize overlay renderer with screen
            self.overlay_renderer = OverlayRenderer(self.screen)
            self.use_embedded_pygame = True
        except pygame.error as e:
            self.logger.error(f"Failed to create Pygame surface: {e}")
            # Fallback to canvas if Pygame embedding fails
            self._create_fallback_canvas()
            
    def _create_fallback_canvas(self):
        """Create a Tkinter canvas as fallback if Pygame embedding fails."""
        self.canvas = tk.Canvas(
            self.camera_frame,
            bg='#1a1a1a',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.use_canvas = True
        self.logger.warning("Using Tkinter Canvas as fallback")
        
    def _create_controls(self):
        """Create control buttons and status indicators."""
        # Button frame
        button_frame = tk.Frame(self.control_panel, bg='#2b2b2b')
        button_frame.pack(side=tk.TOP, pady=10)
        
        # Start/Stop button
        self.start_button = tk.Button(
            button_frame,
            text="Start Camera",
            command=self.toggle_camera,
            font=('Arial', 12, 'bold'),
            bg='#4682b4',
            fg='white',
            activebackground='#5692c4',
            activeforeground='white',
            padx=15,
            pady=8,
            relief=tk.RAISED,
            bd=2,
            cursor='hand2'
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Toggle bubbles button
        self.bubble_button = tk.Button(
            button_frame,
            text="Show Bubbles",
            command=self.toggle_bubbles,
            font=('Arial', 12),
            bg='#6c757d',
            fg='white',
            activebackground='#7c858d',
            activeforeground='white',
            padx=15,
            pady=8,
            relief=tk.RAISED,
            bd=2,
            cursor='hand2'
        )
        self.bubble_button.pack(side=tk.LEFT, padx=5)
        
        # Debug mode button
        self.debug_button = tk.Button(
            button_frame,
            text="Debug",
            command=self.toggle_debug,
            font=('Arial', 10),
            bg='#495057',
            fg='white',
            activebackground='#595961',
            activeforeground='white',
            padx=10,
            pady=5,
            relief=tk.RAISED,
            bd=2,
            cursor='hand2'
        )
        self.debug_button.pack(side=tk.LEFT, padx=5)
        
        # Status frame (bottom)
        status_frame = tk.Frame(self.control_panel, bg='#2b2b2b')
        status_frame.pack(side=tk.TOP, pady=10)
        
        # Status indicators in a row
        # FPS counter
        self.fps_label = tk.Label(
            status_frame,
            text="FPS: 0",
            bg='#2b2b2b',
            fg='#00ff00',
            font=('Arial', 10)
        )
        self.fps_label.pack(side=tk.LEFT, padx=10)
        
        # Detection counter
        self.detection_label = tk.Label(
            status_frame,
            text="Detections: 0",
            bg='#2b2b2b',
            fg='white',
            font=('Arial', 10)
        )
        self.detection_label.pack(side=tk.LEFT, padx=10)
        
        # Camera status
        self.status_label = tk.Label(
            status_frame,
            text="Camera: Inactive",
            bg='#2b2b2b',
            fg='#ff6666',
            font=('Arial', 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Instructions
        info_label = tk.Label(
            self.control_panel,
            text="Camera view opens in separate window (F11 for fullscreen)",
            bg='#2b2b2b',
            fg='#888888',
            font=('Arial', 9, 'italic')
        )
        info_label.pack(side=tk.BOTTOM, pady=5)
        
    def toggle_camera(self):
        """Toggle camera on/off."""
        self.camera_active = not self.camera_active
        
        if self.camera_active:
            # Try to start real camera
            if self.use_real_camera and self.overlay_renderer:
                success = self.overlay_renderer.start_camera()
                if success:
                    self.start_button.config(text="Stop Camera", bg='#dc3545')
                    self.status_label.config(text="Camera: Active", fg='#00ff00')
                    self.logger.info("Real camera started")
                    return
                else:
                    self.logger.warning("Failed to start real camera, falling back to mock")
                    self.use_real_camera = False
                    
            # Fallback to mock camera
            self.start_button.config(text="Stop Camera", bg='#dc3545')
            self.status_label.config(text="Camera: Active (Mock)", fg='#00ff00')
            self.logger.info("Mock camera started")
            
            # Create mock bubbles when using mock camera
            if self.show_bubbles and not self.use_real_camera:
                self.bubble_renderer.create_mock_bubbles(
                    self.screen.get_size(), 
                    count=3
                )
        else:
            self.start_button.config(text="Start Camera", bg='#4682b4')
            self.status_label.config(text="Camera: Inactive", fg='#ff6666')
            self.logger.info("Camera stopped")
            
            # Stop real camera if active
            if self.overlay_renderer:
                self.overlay_renderer.stop_camera()
            
            # Clear bubbles
            self.bubble_renderer.clear_all()
            
    def toggle_bubbles(self):
        """Toggle bubble display."""
        self.show_bubbles = not self.show_bubbles
        
        if self.show_bubbles:
            self.bubble_button.config(text="Hide Bubbles", bg='#28a745')
            self.logger.info("Bubbles enabled")
            
            # Create mock bubbles if using mock camera
            if self.camera_active and not self.use_real_camera:
                self.bubble_renderer.create_mock_bubbles(
                    self.screen.get_size(), 
                    count=3
                )
        else:
            self.bubble_button.config(text="Show Bubbles", bg='#6c757d')
            self.logger.info("Bubbles disabled")
            
            # Clear all bubbles
            if self.overlay_renderer:
                self.overlay_renderer.bubble_renderer.clear_all()
            self.bubble_renderer.clear_all()
            
    def toggle_debug(self):
        """Toggle debug visualization."""
        if self.overlay_renderer:
            self.overlay_renderer.toggle_debug()
            if self.overlay_renderer.show_debug:
                self.debug_button.config(bg='#ffc107')
            else:
                self.debug_button.config(bg='#495057')
            
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        self.logger.info(f"Fullscreen: {self.is_fullscreen}")
        
    def toggle_pygame_fullscreen(self):
        """Toggle fullscreen for Pygame window."""
        self.pygame_fullscreen = not self.pygame_fullscreen
        
        if self.pygame_fullscreen:
            # Get monitor size
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        else:
            # Return to windowed mode
            self.screen = pygame.display.set_mode((self.pygame_width, self.pygame_height))
            
        # Reinitialize overlay renderer with new screen
        if self.overlay_renderer:
            self.overlay_renderer.screen = self.screen
            self.overlay_renderer.screen_size = self.screen.get_size()
            
        self.logger.info(f"Pygame fullscreen: {self.pygame_fullscreen}")
        
    def exit_fullscreen(self):
        """Exit fullscreen mode."""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes('-fullscreen', False)
            
    def update_display(self):
        """Update the camera display."""
        if hasattr(self, 'screen') and self.screen:
            if self.camera_active:
                # Use real camera if available
                if self.use_real_camera and self.overlay_renderer:
                    self.overlay_renderer.render(self.show_bubbles)
                else:
                    # Mock camera feed
                    import time
                    t = time.time()
                    r = int((1 + pygame.math.sin(t)) * 127)
                    g = int((1 + pygame.math.sin(t + 2)) * 127)
                    b = int((1 + pygame.math.sin(t + 4)) * 127)
                    self.screen.fill((r//3, g//3, b//3))
                    
                    # Draw center crosshair
                    width, height = self.screen.get_size()
                    pygame.draw.circle(
                        self.screen,
                        (255, 255, 255),
                        (width // 2, height // 2),
                        50,
                        2
                    )
                    
                    # Draw text
                    font = pygame.font.Font(None, 36)
                    text = font.render("Mock Camera Feed", True, (255, 255, 255))
                    text_rect = text.get_rect(center=(width // 2, height // 2))
                    self.screen.blit(text, text_rect)
                    
                    # Update and draw bubbles for mock camera
                    if self.show_bubbles:
                        self.bubble_renderer.update()
                        self.bubble_renderer.handle_collisions()
                        self.bubble_renderer.draw(self.screen)
            else:
                # Dark screen when inactive
                self.screen.fill((20, 20, 20))
                width, height = self.screen.get_size()
                font = pygame.font.Font(None, 48)
                text = font.render("Camera Inactive", True, (100, 100, 100))
                text_rect = text.get_rect(center=(width // 2, height // 2))
                self.screen.blit(text, text_rect)
                
            pygame.display.flip()
            
    def update_fps(self):
        """Update FPS counter."""
        self.current_fps = self.fps_clock.get_fps()
        self.fps_label.config(text=f"FPS: {self.current_fps:.1f}")
        
        # Update detection counter
        if self.use_real_camera and self.overlay_renderer:
            bubble_count = self.overlay_renderer.bubble_renderer.get_bubble_count()
        else:
            bubble_count = self.bubble_renderer.get_bubble_count()
        self.detection_label.config(text=f"Detections: {bubble_count}")
        
    def run(self):
        """Main application loop."""
        self.running = True
        self.logger.info("Starting main loop")
        
        def update():
            if self.running:
                # Handle Pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.on_close()
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F11:
                            self.toggle_pygame_fullscreen()
                        elif event.key == pygame.K_ESCAPE and self.pygame_fullscreen:
                            self.toggle_pygame_fullscreen()
                
                # Update display
                self.update_display()
                
                # Update FPS
                self.fps_clock.tick(CAMERA_FPS)
                self.update_fps()
                
                # Schedule next update
                self.root.after(1000 // CAMERA_FPS, update)
                
        # Start update loop
        update()
        
        # Start Tkinter main loop
        self.root.mainloop()
        
    def _on_settings_change(self, settings):
        """Handle settings changes from settings panel."""
        # Apply settings to bubble renderer
        # This will be connected when we refactor bubble system to use settings
        self.logger.info("Settings changed - implementation pending")
        
    def on_close(self):
        """Handle window close event."""
        self.logger.info("Closing application")
        self.running = False
        
        # Clean up overlay renderer
        if self.overlay_renderer:
            self.overlay_renderer.cleanup()
            
        pygame.quit()
        self.root.destroy()