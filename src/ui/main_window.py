"""Main application window using Pygame."""

import pygame
import logging
import os
import sys
from typing import Optional

from utils.config import (
    APP_NAME, CAMERA_FPS
)
from bubble_system.bubble_renderer import BubbleRenderer
from ui.overlay_renderer import OverlayRenderer


class MainWindow:
    """Main application window."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.running = False
        self.camera_active = True
        self.show_bubbles = True
        self.fps_clock = pygame.time.Clock()
        self.current_fps = 0
        
        os.environ['SDL_VIDEO_ALLOW_SCREENSAVER'] = '1'
        
        try:
            pygame.display.init()
            pygame.font.init()
        except pygame.error as e:
            self.logger.warning(f"Pygame init warning: {e}")

        self.bubble_renderer = BubbleRenderer()
        self.overlay_renderer = None
        self.use_real_camera = True
        self.pygame_fullscreen = False

        self._create_pygame_window()

    def _create_pygame_window(self):
        """Create a Pygame window."""
        try:
            self.pygame_width = 1024
            self.pygame_height = 768
            self.screen = pygame.display.set_mode((self.pygame_width, self.pygame_height), pygame.RESIZABLE)
            pygame.display.set_caption(f"{APP_NAME} - Camera View")
            
            self.overlay_renderer = OverlayRenderer(self.screen)
            self.logger.info("Created Pygame window")
            
        except pygame.error as e:
            self.logger.error(f"Failed to create Pygame window: {e}")
            sys.exit(1)

    def toggle_debug(self):
        """Toggle debug visualization."""
        if self.overlay_renderer:
            self.overlay_renderer.toggle_debug()
            self.logger.info(f"Debug mode set to: {self.overlay_renderer.show_debug}")
            
    def toggle_pygame_fullscreen(self):
        """Toggle fullscreen for Pygame window."""
        self.pygame_fullscreen = not self.pygame_fullscreen
        
        if self.pygame_fullscreen:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.pygame_width, self.pygame_height), pygame.RESIZABLE)
            
        if self.overlay_renderer:
            self.overlay_renderer.screen = self.screen
            self.overlay_renderer.screen_size = self.screen.get_size()
            
        self.logger.info(f"Pygame fullscreen: {self.pygame_fullscreen}")
        
    def update_display(self):
        """Update the camera display."""
        if hasattr(self, 'screen') and self.screen:
            if self.camera_active:
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
                    
                    width, height = self.screen.get_size()
                    pygame.draw.circle(self.screen, (255, 255, 255), (width // 2, height // 2), 50, 2)
                    
                    font = pygame.font.Font(None, 36)
                    text = font.render("Mock Camera Feed", True, (255, 255, 255))
                    text_rect = text.get_rect(center=(width // 2, height // 2))
                    self.screen.blit(text, text_rect)
                    
                    if self.show_bubbles:
                        self.bubble_renderer.update()
                        self.bubble_renderer.handle_collisions()
                        self.bubble_renderer.draw(self.screen)
            else:
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
        if self.use_real_camera and self.overlay_renderer:
            bubble_count = self.overlay_renderer.bubble_renderer.get_bubble_count()
        else:
            bubble_count = self.bubble_renderer.get_bubble_count()
        
    def run(self):
        """Main application loop."""
        self.running = True
        self.logger.info("Starting main loop")

        if self.use_real_camera and self.overlay_renderer:
            if not self.overlay_renderer.start_camera():
                self.logger.warning("Failed to start real camera, using mock.")
                self.use_real_camera = False

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    if not self.pygame_fullscreen:
                        self.pygame_width = event.w
                        self.pygame_height = event.h
                        self.screen = pygame.display.set_mode((self.pygame_width, self.pygame_height), pygame.RESIZABLE)
                        if self.overlay_renderer:
                            self.overlay_renderer.screen = self.screen
                            self.overlay_renderer.screen_size = self.screen.get_size()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        self.toggle_debug()
                    if event.key == pygame.K_F11:
                        self.toggle_pygame_fullscreen()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            
            self.update_display()
            self.fps_clock.tick(CAMERA_FPS)
            self.update_fps()

        self.on_close()
        
    def on_close(self):
        """Handle window close event."""
        self.logger.info("Closing application")
        
        if self.overlay_renderer:
            self.overlay_renderer.cleanup()
            
        pygame.quit()
