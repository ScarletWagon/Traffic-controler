"""
Enums for traffic simulation system.
"""
from enum import Enum


class Direction(Enum):
    """Cardinal directions for cars and roads."""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class Movement(Enum):
    """Intended car movements at intersections."""
    STRAIGHT = "straight"
    LEFT = "left"
    RIGHT = "right"


class TrafficLightState(Enum):
    """Traffic light states."""
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    GREEN_ARROW = "green_arrow"


class CellType(Enum):
    """Types of cells in the grid map."""
    EMPTY = "empty"
    ROAD = "road"
    INTERSECTION = "intersection"
