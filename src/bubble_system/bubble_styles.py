"""Different bubble style variations."""

import random
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class BubbleStyleVariant:
    """Defines a bubble style variant."""
    name: str
    fill_color: Tuple[int, int, int]
    border_color: Tuple[int, int, int]
    border_width: int
    corner_radius: int
    tail_style: str  # 'straight', 'curved', 'cloud'
    shadow_color: Tuple[int, int, int]
    shadow_offset: Tuple[int, int]
    

# Predefined bubble styles
BUBBLE_STYLES = [
    BubbleStyleVariant(
        name="classic",
        fill_color=(255, 255, 255),
        border_color=(200, 200, 200),
        border_width=2,
        corner_radius=20,
        tail_style="straight",
        shadow_color=(100, 100, 100),
        shadow_offset=(5, 5)
    ),
    BubbleStyleVariant(
        name="soft_blue",
        fill_color=(220, 235, 255),
        border_color=(150, 180, 220),
        border_width=2,
        corner_radius=25,
        tail_style="curved",
        shadow_color=(120, 140, 180),
        shadow_offset=(4, 4)
    ),
    BubbleStyleVariant(
        name="warm_yellow",
        fill_color=(255, 250, 220),
        border_color=(220, 200, 150),
        border_width=2,
        corner_radius=22,
        tail_style="straight",
        shadow_color=(180, 160, 120),
        shadow_offset=(5, 5)
    ),
    BubbleStyleVariant(
        name="mint_green",
        fill_color=(230, 255, 230),
        border_color=(150, 220, 150),
        border_width=2,
        corner_radius=20,
        tail_style="curved",
        shadow_color=(120, 180, 120),
        shadow_offset=(4, 4)
    ),
    BubbleStyleVariant(
        name="lavender",
        fill_color=(240, 230, 255),
        border_color=(200, 180, 220),
        border_width=2,
        corner_radius=24,
        tail_style="straight",
        shadow_color=(160, 140, 180),
        shadow_offset=(5, 5)
    ),
    BubbleStyleVariant(
        name="coral",
        fill_color=(255, 230, 230),
        border_color=(220, 180, 180),
        border_width=2,
        corner_radius=20,
        tail_style="curved",
        shadow_color=(180, 140, 140),
        shadow_offset=(4, 4)
    ),
    BubbleStyleVariant(
        name="cloud",
        fill_color=(245, 245, 245),
        border_color=(180, 180, 180),
        border_width=3,
        corner_radius=30,
        tail_style="cloud",
        shadow_color=(120, 120, 120),
        shadow_offset=(6, 6)
    )
]


def get_random_style() -> BubbleStyleVariant:
    """Get a random bubble style."""
    return random.choice(BUBBLE_STYLES)


def get_style_by_name(name: str) -> BubbleStyleVariant:
    """Get a bubble style by name."""
    for style in BUBBLE_STYLES:
        if style.name == name:
            return style
    return BUBBLE_STYLES[0]  # Default to classic


def get_style_for_person(person_id: str) -> BubbleStyleVariant:
    """Get a consistent style for a person based on their ID."""
    # Use hash to get consistent style per person
    style_index = hash(person_id) % len(BUBBLE_STYLES)
    return BUBBLE_STYLES[style_index]