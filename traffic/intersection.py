"""
Intersection class for traffic simulation.
"""
from typing import Dict, List, Optional, Tuple, Set
from enums import Direction, Movement, TrafficLightState
from car import Car
from traffic_light import TrafficLightController
from road import Road


class Intersection:
    """
    Represents a traffic intersection where roads meet.
    
    Attributes:
        intersection_id: Unique identifier for the intersection
        center_position: Center position of the intersection
        size: Size of the intersection (assumed square)
        traffic_controller: Traffic light controller for this intersection
        connected_roads: Roads connected to this intersection
        intersection_positions: Set of all positions within the intersection
    """
    
    def __init__(self, intersection_id: str, center_position: Tuple[int, int], size: int = 3):
        self.intersection_id = intersection_id
        self.center_position = center_position
        self.size = size
        self.traffic_controller = TrafficLightController(intersection_id)
        self.connected_roads: Dict[Direction, Road] = {}
        self.intersection_positions = self._calculate_intersection_positions()
        self.cars_in_intersection: List[Car] = []
        
        # Create traffic lights for all four directions
        for direction in Direction:
            self.traffic_controller.add_light(direction)
    
    def _calculate_intersection_positions(self) -> Set[Tuple[int, int]]:
        """Calculate all positions that belong to this intersection."""
        positions = set()
        center_row, center_col = self.center_position
        half_size = self.size // 2
        
        for row in range(center_row - half_size, center_row + half_size + 1):
            for col in range(center_col - half_size, center_col + half_size + 1):
                positions.add((row, col))
        
        return positions
    
    def connect_road(self, road: Road, direction: Direction) -> None:
        """
        Connect a road to this intersection.
        
        Args:
            road: Road to connect
            direction: Which side of the intersection the road connects to
        """
        self.connected_roads[direction] = road
    
    def can_car_enter(self, car: Car, from_direction: Direction) -> bool:
        """
        Check if a car can enter the intersection.
        
        Args:
            car: Car wanting to enter
            from_direction: Direction the car is coming from
            
        Returns:
            True if car can enter
        """
        # Check traffic light
        light_state = self.traffic_controller.lights[from_direction].state
        
        if car.intended_movement == Movement.STRAIGHT:
            if not self.traffic_controller.lights[from_direction].can_go_straight():
                return False
        elif car.intended_movement == Movement.LEFT:
            if not self.traffic_controller.lights[from_direction].can_turn_left():
                return False
        elif car.intended_movement == Movement.RIGHT:
            if not self.traffic_controller.lights[from_direction].can_turn_right():
                return False
        
        # Check if intersection has space
        next_pos = car.get_next_position()
        return self._is_intersection_position_free(next_pos)
    
    def _is_intersection_position_free(self, position: Tuple[int, int]) -> bool:
        """Check if a position in the intersection is free."""
        if position not in self.intersection_positions:
            return False
        
        for car in self.cars_in_intersection:
            if car.position == position:
                return False
        
        return True
    
    def add_car_to_intersection(self, car: Car) -> bool:
        """
        Add a car to the intersection.
        
        Args:
            car: Car to add
            
        Returns:
            True if car was added successfully
        """
        if car.position in self.intersection_positions and car not in self.cars_in_intersection:
            self.cars_in_intersection.append(car)
            return True
        return False
    
    def remove_car_from_intersection(self, car: Car) -> bool:
        """
        Remove a car from the intersection.
        
        Args:
            car: Car to remove
            
        Returns:
            True if car was removed
        """
        if car in self.cars_in_intersection:
            self.cars_in_intersection.remove(car)
            return True
        return False
    
    def get_exit_direction(self, car: Car, entry_direction: Direction) -> Direction:
        """
        Determine which direction a car should exit based on its intended movement.
        
        Args:
            car: Car in the intersection
            entry_direction: Direction the car entered from
            
        Returns:
            Direction the car should exit to
        """
        if car.intended_movement == Movement.STRAIGHT:
            # Continue in the same direction
            return entry_direction
        elif car.intended_movement == Movement.RIGHT:
            # Turn right (clockwise)
            if entry_direction == Direction.NORTH:
                return Direction.EAST
            elif entry_direction == Direction.EAST:
                return Direction.SOUTH
            elif entry_direction == Direction.SOUTH:
                return Direction.WEST
            elif entry_direction == Direction.WEST:
                return Direction.NORTH
        elif car.intended_movement == Movement.LEFT:
            # Turn left (counter-clockwise)
            if entry_direction == Direction.NORTH:
                return Direction.WEST
            elif entry_direction == Direction.WEST:
                return Direction.SOUTH
            elif entry_direction == Direction.SOUTH:
                return Direction.EAST
            elif entry_direction == Direction.EAST:
                return Direction.NORTH
        
        return entry_direction  # Fallback
    
    def process_car_in_intersection(self, car: Car, entry_direction: Direction) -> Optional[Direction]:
        """
        Process a car that's currently in the intersection.
        
        Args:
            car: Car to process
            entry_direction: Direction the car entered from
            
        Returns:
            Direction the car should exit to, or None if car should stay
        """
        exit_direction = self.get_exit_direction(car, entry_direction)
        
        # Check if the car has reached the exit point
        center_row, center_col = self.center_position
        
        if exit_direction == Direction.NORTH and car.position[0] <= center_row - 1:
            return exit_direction
        elif exit_direction == Direction.SOUTH and car.position[0] >= center_row + 1:
            return exit_direction
        elif exit_direction == Direction.EAST and car.position[1] >= center_col + 1:
            return exit_direction
        elif exit_direction == Direction.WEST and car.position[1] <= center_col - 1:
            return exit_direction
        
        return None  # Car should continue moving through intersection
    
    def get_state_info(self) -> Dict:
        """Get current state information for ML observation."""
        return {
            'intersection_id': self.intersection_id,
            'cars_count': len(self.cars_in_intersection),
            'traffic_lights': self.traffic_controller.get_state_info(),
            'car_positions': [car.position for car in self.cars_in_intersection]
        }
    
    def update(self) -> None:
        """Update the intersection (mainly traffic lights)."""
        self.traffic_controller.update()
    
    def __str__(self) -> str:
        return f"Intersection({self.intersection_id}) at {self.center_position} ({len(self.cars_in_intersection)} cars)"
