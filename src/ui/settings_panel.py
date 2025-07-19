"""Settings panel for configuring bubble appearance and behavior."""

import tkinter as tk
from tkinter import ttk, colorchooser, font
import logging

from utils.config import (
    BUBBLE_COLOR, TEXT_COLOR, DEFAULT_FONT_SIZE,
    BUBBLE_ALPHA, BUBBLE_MIN_SIZE, BUBBLE_MAX_SIZE,
    BUBBLE_SWAY_AMPLITUDE, BUBBLE_SWAY_SPEED
)


class SettingsPanel:
    """Collapsible settings panel for the application."""
    
    def __init__(self, parent, on_settings_change=None):
        self.logger = logging.getLogger(__name__)
        self.parent = parent
        self.on_settings_change = on_settings_change
        self.is_expanded = False
        
        # Current settings
        self.settings = {
            'bubble_color': BUBBLE_COLOR,
            'text_color': TEXT_COLOR,
            'font_size': DEFAULT_FONT_SIZE,
            'bubble_alpha': BUBBLE_ALPHA,
            'bubble_min_width': BUBBLE_MIN_SIZE[0],
            'bubble_min_height': BUBBLE_MIN_SIZE[1],
            'bubble_max_width': BUBBLE_MAX_SIZE[0],
            'bubble_max_height': BUBBLE_MAX_SIZE[1],
            'sway_amplitude': BUBBLE_SWAY_AMPLITUDE,
            'sway_speed': BUBBLE_SWAY_SPEED,
            'show_shadows': True,
            'animation_speed': 1.0
        }
        
        self._create_panel()
        
    def _create_panel(self):
        """Create the settings panel UI."""
        # Main container
        self.panel_frame = tk.Frame(self.parent, bg='#3a3a3a', width=300)
        self.panel_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.panel_frame.pack_propagate(False)
        
        # Toggle button
        self.toggle_button = tk.Button(
            self.panel_frame,
            text="◀ Settings",
            command=self.toggle_panel,
            bg='#4a4a4a',
            fg='white',
            font=('Arial', 10),
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2'
        )
        self.toggle_button.pack(fill=tk.X)
        
        # Settings container (initially hidden)
        self.settings_container = tk.Frame(self.panel_frame, bg='#3a3a3a')
        
        # Create sections
        self._create_appearance_section()
        self._create_animation_section()
        self._create_performance_section()
        
        # Initially collapsed
        self.panel_frame.config(width=40)
        
    def _create_appearance_section(self):
        """Create appearance settings section."""
        section = self._create_section("Appearance")
        
        # Bubble color
        color_frame = tk.Frame(section, bg='#3a3a3a')
        color_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            color_frame,
            text="Bubble Color:",
            bg='#3a3a3a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT)
        
        self.bubble_color_btn = tk.Button(
            color_frame,
            text="    ",
            bg=self._rgb_to_hex(self.settings['bubble_color']),
            command=self._choose_bubble_color,
            width=3,
            cursor='hand2'
        )
        self.bubble_color_btn.pack(side=tk.RIGHT, padx=5)
        
        # Text color
        text_color_frame = tk.Frame(section, bg='#3a3a3a')
        text_color_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            text_color_frame,
            text="Text Color:",
            bg='#3a3a3a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT)
        
        self.text_color_btn = tk.Button(
            text_color_frame,
            text="    ",
            bg=self._rgb_to_hex(self.settings['text_color']),
            command=self._choose_text_color,
            width=3,
            cursor='hand2'
        )
        self.text_color_btn.pack(side=tk.RIGHT, padx=5)
        
        # Font size
        font_frame = tk.Frame(section, bg='#3a3a3a')
        font_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            font_frame,
            text="Font Size:",
            bg='#3a3a3a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT)
        
        self.font_size_var = tk.IntVar(value=self.settings['font_size'])
        self.font_size_scale = ttk.Scale(
            font_frame,
            from_=12,
            to=24,
            variable=self.font_size_var,
            orient=tk.HORIZONTAL,
            command=self._on_font_size_change
        )
        self.font_size_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Transparency
        alpha_frame = tk.Frame(section, bg='#3a3a3a')
        alpha_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            alpha_frame,
            text="Transparency:",
            bg='#3a3a3a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT)
        
        self.alpha_var = tk.IntVar(value=self.settings['bubble_alpha'])
        self.alpha_scale = ttk.Scale(
            alpha_frame,
            from_=100,
            to=255,
            variable=self.alpha_var,
            orient=tk.HORIZONTAL,
            command=self._on_alpha_change
        )
        self.alpha_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
    def _create_animation_section(self):
        """Create animation settings section."""
        section = self._create_section("Animation")
        
        # Sway amplitude
        sway_frame = tk.Frame(section, bg='#3a3a3a')
        sway_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            sway_frame,
            text="Sway Amount:",
            bg='#3a3a3a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT)
        
        self.sway_var = tk.IntVar(value=self.settings['sway_amplitude'])
        self.sway_scale = ttk.Scale(
            sway_frame,
            from_=0,
            to=20,
            variable=self.sway_var,
            orient=tk.HORIZONTAL,
            command=self._on_sway_change
        )
        self.sway_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Animation speed
        speed_frame = tk.Frame(section, bg='#3a3a3a')
        speed_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            speed_frame,
            text="Animation Speed:",
            bg='#3a3a3a',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT)
        
        self.speed_var = tk.DoubleVar(value=self.settings['animation_speed'])
        self.speed_scale = ttk.Scale(
            speed_frame,
            from_=0.5,
            to=2.0,
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            command=self._on_speed_change
        )
        self.speed_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Show shadows checkbox
        self.shadow_var = tk.BooleanVar(value=self.settings['show_shadows'])
        self.shadow_check = tk.Checkbutton(
            section,
            text="Show Shadows",
            variable=self.shadow_var,
            command=self._on_shadow_toggle,
            bg='#3a3a3a',
            fg='white',
            selectcolor='#3a3a3a',
            font=('Arial', 9)
        )
        self.shadow_check.pack(anchor='w', pady=5)
        
    def _create_performance_section(self):
        """Create performance settings section."""
        section = self._create_section("Performance")
        
        # Detection sensitivity placeholder
        tk.Label(
            section,
            text="Detection Sensitivity:",
            bg='#3a3a3a',
            fg='#888',
            font=('Arial', 9)
        ).pack(anchor='w', pady=5)
        
        tk.Label(
            section,
            text="(Available when CV integrated)",
            bg='#3a3a3a',
            fg='#666',
            font=('Arial', 8, 'italic')
        ).pack(anchor='w')
        
    def _create_section(self, title):
        """Create a settings section with title."""
        # Section container
        section_frame = tk.Frame(self.settings_container, bg='#3a3a3a')
        section_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Section title
        title_label = tk.Label(
            section_frame,
            text=title,
            bg='#3a3a3a',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Separator
        separator = tk.Frame(section_frame, height=1, bg='#555')
        separator.pack(fill=tk.X, pady=(0, 10))
        
        return section_frame
        
    def toggle_panel(self):
        """Toggle settings panel visibility."""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.panel_frame.config(width=300)
            self.settings_container.pack(fill=tk.BOTH, expand=True, pady=10)
            self.toggle_button.config(text="Settings ▶")
        else:
            self.settings_container.pack_forget()
            self.panel_frame.config(width=40)
            self.toggle_button.config(text="◀ Settings")
            
    def _rgb_to_hex(self, rgb):
        """Convert RGB tuple to hex color string."""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
    def _hex_to_rgb(self, hex_color):
        """Convert hex color string to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def _choose_bubble_color(self):
        """Open color chooser for bubble color."""
        color = colorchooser.askcolor(
            initialcolor=self._rgb_to_hex(self.settings['bubble_color']),
            title="Choose Bubble Color"
        )
        if color[1]:  # color[1] is hex string
            self.settings['bubble_color'] = color[0]  # color[0] is RGB tuple
            self.bubble_color_btn.config(bg=color[1])
            self._notify_change()
            
    def _choose_text_color(self):
        """Open color chooser for text color."""
        color = colorchooser.askcolor(
            initialcolor=self._rgb_to_hex(self.settings['text_color']),
            title="Choose Text Color"
        )
        if color[1]:
            self.settings['text_color'] = color[0]
            self.text_color_btn.config(bg=color[1])
            self._notify_change()
            
    def _on_font_size_change(self, value):
        """Handle font size change."""
        self.settings['font_size'] = int(float(value))
        self._notify_change()
        
    def _on_alpha_change(self, value):
        """Handle transparency change."""
        self.settings['bubble_alpha'] = int(float(value))
        self._notify_change()
        
    def _on_sway_change(self, value):
        """Handle sway amplitude change."""
        self.settings['sway_amplitude'] = int(float(value))
        self._notify_change()
        
    def _on_speed_change(self, value):
        """Handle animation speed change."""
        self.settings['animation_speed'] = float(value)
        self._notify_change()
        
    def _on_shadow_toggle(self):
        """Handle shadow toggle."""
        self.settings['show_shadows'] = self.shadow_var.get()
        self._notify_change()
        
    def _notify_change(self):
        """Notify parent of settings change."""
        if self.on_settings_change:
            self.on_settings_change(self.settings)
            self.logger.debug(f"Settings updated: {self.settings}")
            
    def get_settings(self):
        """Get current settings."""
        return self.settings.copy()