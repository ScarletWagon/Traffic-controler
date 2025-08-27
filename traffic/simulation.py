"""
Traffic simulation engine that coordinates all components.
"""
import random
from typing import Dict, List, Tuple, Optional, Set
from enums import Direction, Movement, CellType, TrafficLightState
from car import Car
from road import Road
from intersection import Intersection
from traffic_light import TrafficLightController


class TrafficSimulation:
    """
    Main simulation engine that coordinates cars, roads, intersections, and traffic lights.
    
    Attributes:
        grid_size: Size of the simulation grid (width, height)
        roads: Dictionary of all roads in the simulation
        intersections: Dictionary of all intersections in the simulation
        cars: List of all cars in the simulation
        tick_count: Current simulation tick
        max_car_speed: Maximum blocks a car can move per tick
    """
    
    def __init__(self, grid_size: Tuple[int, int] = (20, 20)):
        self.grid_size = grid_size
        self.roads: Dict[str, Road] = {}
        self.intersections: Dict[str, Intersection] = {}
        self.cars: List[Car] = []
        self.tick_count = 0
        self.max_car_speed = 2
        
        # Track which cars entered from which direction (for intersection processing)
        self.car_entry_directions: Dict[str, Direction] = {}
    
    def add_road(self, road: Road) -> None:
        """Add a road to the simulation."""
        self.roads[road.road_id] = road
    
    def add_intersection(self, intersection: Intersection) -> None:
        """Add an intersection to the simulation."""
        self.intersections[intersection.intersection_id] = intersection
    
    def add_car(self, car: Car, road_id: str, lane_num: int = 0) -> bool:
        """
        Add a car to the simulation on a specific road.
        
        Args:
            car: Car to add
            road_id: ID of the road to place the car on
            lane_num: Lane number to place the car in
            
        Returns:
            True if car was added successfully
        """
        if road_id in self.roads:
            success = self.roads[road_id].add_car(car, lane_num)
            if success:
                self.cars.append(car)
            return success
        return False
    
    def remove_car(self, car: Car) -> None:
        """Remove a car from the simulation."""
        if car in self.cars:
            self.cars.remove(car)
            
            # Remove from roads
            for road in self.roads.values():
                road.remove_car(car)
            
            # Remove from intersections
            for intersection in self.intersections.values():
                intersection.remove_car_from_intersection(car)
            
            # Clean up entry direction tracking
            if car.car_id in self.car_entry_directions:
                del self.car_entry_directions[car.car_id]
    
    def get_car_at_position(self, position: Tuple[int, int]) -> Optional[Car]:
        """Get the car at a specific position."""
        # Check roads
        for road in self.roads.values():
            car = road.get_car_at_position(position)
            if car:
                return car
        
        # Check intersections
        for intersection in self.intersections.values():
            for car in intersection.cars_in_intersection:
                if car.position == position:
                    return car
        
        return None
    
    def is_position_free(self, position: Tuple[int, int]) -> bool:
        """Check if a position is free (no car there)."""
        return self.get_car_at_position(position) is None
    
    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if a position is within the grid bounds."""
        row, col = position
        return 0 <= row < self.grid_size[1] and 0 <= col < self.grid_size[0]
    
    def find_car_location(self, car: Car) -> Tuple[Optional[str], Optional[str]]:
        """
        Find which road or intersection a car is currently on.
        
        Returns:
            Tuple of (road_id, intersection_id) - one will be None
        """
        # Check roads
        for road_id, road in self.roads.items():
            if car in road.get_all_cars():
                return (road_id, None)
        
        # Check intersections
        for intersection_id, intersection in self.intersections.items():
            if car in intersection.cars_in_intersection:
                return (None, intersection_id)
        
        return (None, None)
    
    def move_car(self, car: Car) -> bool:
        """
        Attempt to move a car forward based on traffic rules.
        
        Args:
            car: Car to move
            
        Returns:
            True if car moved, False if blocked
        """
        road_id, intersection_id = self.find_car_location(car)
        
        if road_id:
            return self._move_car_on_road(car, road_id)
        elif intersection_id:
            return self._move_car_in_intersection(car, intersection_id)
        else:
            # Car is not on any road or intersection - this shouldn't happen
            return False
    
    def _move_car_on_road(self, car: Car, road_id: str) -> bool:
        """Move a car that's currently on a road."""
        road = self.roads[road_id]
        
        # Calculate how far the car can move (up to max_speed)
        distance = min(self.max_car_speed, 1)  # Start with 1 block for simplicity
        
        for dist in range(1, distance + 1):
            next_pos = car.get_next_position(dist)
            
            if not self.is_valid_position(next_pos):
                # Car would go out of bounds
                break
            
            # Check if next position is an intersection
            intersection = self._get_intersection_at_position(next_pos)
            if intersection:
                # Car wants to enter intersection
                entry_direction = car.direction
                if intersection.can_car_enter(car, entry_direction):
                    # Move car to intersection
                    road.remove_car(car)
                    car.move_to(next_pos)
                    intersection.add_car_to_intersection(car)
                    self.car_entry_directions[car.car_id] = entry_direction
                    return True
                else:
                    # Blocked by traffic light or intersection full
                    car.increment_wait_time()
                    return False
            
            # Check if next position is free on the road
            if not self.is_position_free(next_pos):
                # Blocked by another car
                car.increment_wait_time()
                return False
            
            # Move car forward
            car.move_to(next_pos)
            return True
        
        # Couldn't move
        car.increment_wait_time()
        return False
    
    def _move_car_in_intersection(self, car: Car, intersection_id: str) -> bool:
        """Move a car that's currently in an intersection."""
        intersection = self.intersections[intersection_id]
        entry_direction = self.car_entry_directions.get(car.car_id, car.direction)
        
        # Check if car should exit intersection
        exit_direction = intersection.process_car_in_intersection(car, entry_direction)
        
        if exit_direction:
            # Car should exit to a road
            exit_road = intersection.connected_roads.get(exit_direction)
            if exit_road:
                next_pos = car.get_next_position()
                if exit_road.is_position_free(next_pos):
                    # Move car to the exit road
                    intersection.remove_car_from_intersection(car)
                    car.turn(exit_direction)  # Update car's direction
                    car.move_to(next_pos)
                    exit_road.add_car(car, car.lane)
                    
                    # Clean up entry direction tracking
                    if car.car_id in self.car_entry_directions:
                        del self.car_entry_directions[car.car_id]
                    
                    return True
                else:
                    # Exit road is blocked
                    car.increment_wait_time()
                    return False
        
        # Continue moving through intersection
        next_pos = car.get_next_position()
        if (next_pos in intersection.intersection_positions and 
            intersection._is_intersection_position_free(next_pos)):
            car.move_to(next_pos)
            return True
        
        # Can't move
        car.increment_wait_time()
        return False
    
    def _get_intersection_at_position(self, position: Tuple[int, int]) -> Optional[Intersection]:
        """Get the intersection at a specific position."""
        for intersection in self.intersections.values():
            if position in intersection.intersection_positions:
                return intersection
        return None
    
    def tick(self) -> None:
        """
        Perform one simulation tick.
        Updates traffic lights and attempts to move all cars.
        """
        self.tick_count += 1
        
        # Update traffic lights
        for intersection in self.intersections.values():
            intersection.traffic_controller.update_automatic_cycle()
            intersection.update()
        
        # Shuffle cars to avoid movement order bias
        cars_to_move = self.cars.copy()
        random.shuffle(cars_to_move)
        
        # Attempt to move each car
        for car in cars_to_move:
            self.move_car(car)
    
    def get_simulation_state(self) -> Dict:
        """Get current simulation state for ML observation."""
        return {
            'tick': self.tick_count,
            'total_cars': len(self.cars),
            'intersections': {
                intersection_id: intersection.get_state_info()
                for intersection_id, intersection in self.intersections.items()
            },
            'car_wait_times': {car.car_id: car.wait_time for car in self.cars},
            'average_wait_time': sum(car.wait_time for car in self.cars) / len(self.cars) if self.cars else 0
        }
    
    def set_traffic_light(self, intersection_id: str, direction: Direction, state: TrafficLightState) -> bool:
        """
        Set a traffic light state (for ML agent control).
        
        Args:
            intersection_id: ID of the intersection
            direction: Direction of the light to control
            state: New state for the light
            
        Returns:
            True if light was set successfully
        """
        if intersection_id in self.intersections:
            self.intersections[intersection_id].traffic_controller.set_light_state(direction, state)
            return True
        return False
    
    def create_simple_four_way_intersection(self, center: Tuple[int, int] = (10, 10)) -> str:
        """
        Create a simple four-way intersection with roads for testing.
        
        Args:
            center: Center position of the intersection
            
        Returns:
            ID of the created intersection
        """
        intersection_id = "main_intersection"
        intersection = Intersection(intersection_id, center, size=3)
        
        # Create roads connecting to the intersection
        center_row, center_col = center
        
        # North road (cars going south toward intersection)
        north_road = Road("north_road", (center_row - 6, center_col), (center_row - 2, center_col), Direction.SOUTH, 2)
        
        # South road (cars going north toward intersection)
        south_road = Road("south_road", (center_row + 2, center_col), (center_row + 6, center_col), Direction.NORTH, 2)
        
        # East road (cars going west toward intersection)
        east_road = Road("east_road", (center_row, center_col + 2), (center_row, center_col + 6), Direction.WEST, 2)
        
        # West road (cars going east toward intersection)
        west_road = Road("west_road", (center_row, center_col - 6), (center_row, center_col - 2), Direction.EAST, 2)
        
        # Add roads to simulation
        self.add_road(north_road)
        self.add_road(south_road)
        self.add_road(east_road)
        self.add_road(west_road)
        
        # Connect roads to intersection
        intersection.connect_road(north_road, Direction.NORTH)
        intersection.connect_road(south_road, Direction.SOUTH)
        intersection.connect_road(east_road, Direction.EAST)
        intersection.connect_road(west_road, Direction.WEST)
        
        # Add intersection to simulation
        self.add_intersection(intersection)
        
        return intersection_id
    
    def __str__(self) -> str:
        return f"TrafficSimulation(tick={self.tick_count}, cars={len(self.cars)}, intersections={len(self.intersections)})"
