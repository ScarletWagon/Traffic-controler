"""
Car class for traffic simulation.
"""
from typing import Optional, Tuple
from enums import Direction, Movement


class Car:
    """
    Represents a car in the traffic simulation.
    
    Attributes:
        car_id: Unique identifier for the car
        position: Current position on the grid (row, column)
        direction: Current direction the car is facing
        intended_movement: What the car wants to do at the next intersection
        lane: Current lane number (0-based from rightmost lane)
        max_speed: Maximum blocks the car can move per tick
        wait_time: How long the car has been waiting (for ML optimization)
    """
    
    def __init__(
        self, 
        car_id: str, 
        position: Tuple[int, int], 
        direction: Direction,
        intended_movement: Movement = Movement.STRAIGHT,
        lane: int = 0,
        max_speed: int = 2
    ):
        self.car_id = car_id
        self.position = position
        self.direction = direction
        self.intended_movement = intended_movement
        self.lane = lane
        self.max_speed = max_speed
        self.wait_time = 0
        self.target_position: Optional[Tuple[int, int]] = None
    
    def get_next_position(self, distance: int = 1) -> Tuple[int, int]:
        """
        Calculate the next position based on current direction and distance.
        
        Args:
            distance: Number of blocks to move forward
            
        Returns:
            Tuple of (row, column) for the next position
        """
        row, col = self.position
        
        if self.direction == Direction.NORTH:
            return (row - distance, col)
        elif self.direction == Direction.SOUTH:
            return (row + distance, col)
        elif self.direction == Direction.EAST:
            return (row, col + distance)
        elif self.direction == Direction.WEST:
            return (row, col - distance)
        
        return self.position
    
    def move_to(self, new_position: Tuple[int, int]) -> None:
        """
        Move the car to a new position.
        
        Args:
            new_position: The new (row, column) position
        """
        self.position = new_position
        self.wait_time = 0  # Reset wait time when moving
    
    def increment_wait_time(self) -> None:
        """Increment the wait time when the car cannot move."""
        self.wait_time += 1
    
    def turn(self, new_direction: Direction) -> None:
        """
        Change the car's direction (for turning at intersections).
        
        Args:
            new_direction: The new direction to face
        """
        self.direction = new_direction
    
    def __str__(self) -> str:
        return f"Car({self.car_id}) at {self.position} facing {self.direction.value}"
    
    def __repr__(self) -> str:
        return self.__str__()
