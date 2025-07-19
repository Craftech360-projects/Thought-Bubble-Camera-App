"""Thought bubble class with animations and rendering."""

import pygame
import math
import time
import random
from typing import Tuple, Optional
from dataclasses import dataclass

from utils.config import (
    BUBBLE_MIN_SIZE, BUBBLE_MAX_SIZE, BUBBLE_PADDING,
    BUBBLE_TAIL_HEIGHT, BUBBLE_COLOR, BUBBLE_ALPHA,
    TEXT_COLOR, DEFAULT_FONT_SIZE, BUBBLE_SWAY_AMPLITUDE,
    BUBBLE_SWAY_SPEED, BUBBLE_FADE_DURATION
)
from bubble_system.bubble_styles import BubbleStyleVariant, get_style_for_person


@dataclass
class BubbleStyle:
    """Bubble visual style configuration."""
    fill_color: Tuple[int, int, int] = BUBBLE_COLOR
    border_color: Tuple[int, int, int] = (200, 200, 200)
    border_width: int = 2
    corner_radius: int = 20
    tail_width: int = 30
    shadow_offset: Tuple[int, int] = (5, 5)
    shadow_alpha: int = 100


class Bubble:
    """Animated thought bubble with text content."""
    
    def __init__(self, bubble_id: str, position: Tuple[int, int], text: str, style_variant: Optional[BubbleStyleVariant] = None):
        self.id = bubble_id
        self.base_position = position  # Base position (follows person)
        self.current_position = list(position)  # Current animated position
        self.text = text
        
        # Use provided style or get one based on person ID
        if style_variant:
            self.style_variant = style_variant
        else:
            self.style_variant = get_style_for_person(bubble_id)
            
        # Create BubbleStyle from variant
        self.style = BubbleStyle(
            fill_color=self.style_variant.fill_color,
            border_color=self.style_variant.border_color,
            border_width=self.style_variant.border_width,
            corner_radius=self.style_variant.corner_radius,
            shadow_offset=self.style_variant.shadow_offset
        )
        
        # Animation state
        self.creation_time = time.time()
        self.is_visible = True
        self.fade_start_time = None
        self.sway_offset = 0
        self.sway_phase = random.uniform(0, 2 * math.pi)  # Random start phase
        self.bounce_offset = 0
        self.bounce_velocity = 0
        
        # Calculate bubble size based on text
        self.font = pygame.font.Font(None, DEFAULT_FONT_SIZE)
        self._calculate_size()
        
        # Pre-render surfaces for performance
        self._render_bubble_surface()
        
    def _calculate_size(self):
        """Calculate bubble size based on text content."""
        # Measure text
        lines = self._wrap_text(self.text, 250)  # Max width 250px
        max_width = 0
        total_height = 0
        
        for line in lines:
            text_surface = self.font.render(line, True, TEXT_COLOR)
            max_width = max(max_width, text_surface.get_width())
            total_height += text_surface.get_height() + 5  # Line spacing
            
        # Add padding
        self.width = max_width + BUBBLE_PADDING * 2
        self.height = total_height + BUBBLE_PADDING * 2
        
        # Constrain to min/max sizes
        self.width = max(BUBBLE_MIN_SIZE[0], min(self.width, BUBBLE_MAX_SIZE[0]))
        self.height = max(BUBBLE_MIN_SIZE[1], min(self.height, BUBBLE_MAX_SIZE[1]))
        
        self.text_lines = lines
        
    def _wrap_text(self, text: str, max_width: int) -> list:
        """Wrap text to fit within max width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font.render(test_line, True, TEXT_COLOR)
            
            if test_surface.get_width() > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
                
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
        
    def _render_bubble_surface(self):
        """Pre-render the bubble surface for performance."""
        # Create surface with alpha channel
        self.surface = pygame.Surface(
            (self.width + 10, self.height + BUBBLE_TAIL_HEIGHT + 10),
            pygame.SRCALPHA
        )
        
        # Draw shadow
        shadow_rect = pygame.Rect(
            self.style.shadow_offset[0],
            self.style.shadow_offset[1],
            self.width,
            self.height
        )
        shadow_color = (*self.style.border_color, self.style.shadow_alpha)
        pygame.draw.rect(
            self.surface,
            shadow_color,
            shadow_rect,
            border_radius=self.style.corner_radius
        )
        
        # Draw main bubble
        bubble_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(
            self.surface,
            (*self.style.fill_color, BUBBLE_ALPHA),
            bubble_rect,
            border_radius=self.style.corner_radius
        )
        
        # Draw border
        pygame.draw.rect(
            self.surface,
            self.style.border_color,
            bubble_rect,
            width=self.style.border_width,
            border_radius=self.style.corner_radius
        )
        
        # Draw tail based on style
        if self.style_variant.tail_style == "curved":
            # Draw curved tail
            self._draw_curved_tail(self.surface)
        elif self.style_variant.tail_style == "cloud":
            # Draw cloud-style tail with circles
            self._draw_cloud_tail(self.surface)
        else:
            # Draw straight tail
            tail_points = [
                (self.width // 2 - self.style.tail_width // 2, self.height - 2),
                (self.width // 2 + self.style.tail_width // 2, self.height - 2),
                (self.width // 2, self.height + BUBBLE_TAIL_HEIGHT)
            ]
            pygame.draw.polygon(
                self.surface,
                (*self.style.fill_color, BUBBLE_ALPHA),
                tail_points
            )
            pygame.draw.polygon(
                self.surface,
                self.style.border_color,
                tail_points,
                width=self.style.border_width
            )
        
        # Render text
        y_offset = BUBBLE_PADDING
        for line in self.text_lines:
            text_surface = self.font.render(line, True, TEXT_COLOR)
            text_rect = text_surface.get_rect()
            text_rect.centerx = self.width // 2
            text_rect.y = y_offset
            self.surface.blit(text_surface, text_rect)
            y_offset += text_surface.get_height() + 5
            
    def update(self, target_position: Optional[Tuple[int, int]] = None):
        """Update bubble position and animations."""
        current_time = time.time()
        
        # Update base position if provided
        if target_position:
            # Check if position changed significantly (for bounce effect)
            dx = target_position[0] - self.base_position[0]
            dy = target_position[1] - self.base_position[1]
            if abs(dx) > 5 or abs(dy) > 5:
                self.bounce_velocity = -3  # Start bounce
                
            self.base_position = target_position
            
        # Calculate sway animation with unique phase
        sway_phase = current_time * BUBBLE_SWAY_SPEED + self.sway_phase
        self.sway_offset = math.sin(sway_phase) * BUBBLE_SWAY_AMPLITUDE
        
        # Update bounce animation
        self.bounce_velocity += 0.5  # Gravity
        self.bounce_offset += self.bounce_velocity
        
        # Dampen bounce
        if self.bounce_offset > 0:
            self.bounce_offset = 0
            self.bounce_velocity = 0
        
        # Smooth position interpolation
        interpolation_speed = 0.15
        self.current_position[0] += (self.base_position[0] - self.current_position[0]) * interpolation_speed
        self.current_position[1] += (self.base_position[1] - self.current_position[1]) * interpolation_speed
        
        # Handle fade animation
        if self.fade_start_time:
            fade_progress = (current_time - self.fade_start_time) / BUBBLE_FADE_DURATION
            if fade_progress >= 1.0:
                self.is_visible = False
                
    
            
    def get_alpha(self) -> int:
        """Get current alpha value based on fade state."""
        return BUBBLE_ALPHA
            
    def draw(self, screen: pygame.Surface):
        """Draw the bubble on the screen."""
        if not self.is_visible:
            return
            
        # Calculate final position with sway and bounce
        draw_x = int(self.current_position[0] + self.sway_offset - self.width // 2)
        draw_y = int(self.current_position[1] - self.height - BUBBLE_TAIL_HEIGHT + self.bounce_offset)
        
        # Apply fade alpha
        alpha = self.get_alpha()
        if alpha < 255:
            temp_surface = self.surface.copy()
            temp_surface.set_alpha(alpha)
            screen.blit(temp_surface, (draw_x, draw_y))
        else:
            screen.blit(self.surface, (draw_x, draw_y))
            
    def get_bounds(self) -> pygame.Rect:
        """Get the bounding rectangle of the bubble."""
        x = int(self.current_position[0] + self.sway_offset - self.width // 2)
        y = int(self.current_position[1] - self.height - BUBBLE_TAIL_HEIGHT + self.bounce_offset)
        return pygame.Rect(x, y, self.width, self.height + BUBBLE_TAIL_HEIGHT)
        
    def _draw_curved_tail(self, surface):
        """Draw a curved tail using bezier curve approximation."""
        start_x = self.width // 2
        start_y = self.height - 2
        end_x = self.width // 2
        end_y = self.height + BUBBLE_TAIL_HEIGHT
        
        # Control points for curve
        ctrl1_x = start_x - 10
        ctrl1_y = start_y + 10
        ctrl2_x = end_x + 5
        ctrl2_y = end_y - 5
        
        # Draw filled curved tail
        points = []
        for t in range(0, 11):
            t = t / 10.0
            x = (1-t)**3 * start_x + 3*(1-t)**2*t * ctrl1_x + 3*(1-t)*t**2 * ctrl2_x + t**3 * end_x
            y = (1-t)**3 * start_y + 3*(1-t)**2*t * ctrl1_y + 3*(1-t)*t**2 * ctrl2_y + t**3 * end_y
            points.append((int(x), int(y)))
            
        # Mirror points for other side
        mirror_points = [(self.width - p[0], p[1]) for p in reversed(points[1:-1])]
        all_points = points + mirror_points
        
        if len(all_points) > 2:
            pygame.draw.polygon(surface, (*self.style.fill_color, BUBBLE_ALPHA), all_points)
            pygame.draw.polygon(surface, self.style.border_color, all_points, width=self.style.border_width)
            
    def _draw_cloud_tail(self, surface):
        """Draw a cloud-style tail with circles."""
        # Draw small circles leading to tail point
        positions = [
            (self.width // 2, self.height),
            (self.width // 2 - 5, self.height + 8),
            (self.width // 2 + 3, self.height + 15),
            (self.width // 2, self.height + BUBBLE_TAIL_HEIGHT - 5)
        ]
        
        radii = [8, 6, 5, 4]
        
        for pos, radius in zip(positions, radii):
            pygame.draw.circle(
                surface,
                (*self.style.fill_color, BUBBLE_ALPHA),
                pos,
                radius
            )
            pygame.draw.circle(
                surface,
                self.style.border_color,
                pos,
                radius,
                width=self.style.border_width
            )