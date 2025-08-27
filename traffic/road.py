"""
Road class for traffic simulation.
"""
from typing import List, Dict, Optional, Tuple, Set
from enums import Direction, CellType
from car import Car


class Lane:
    """
    Represents a single lane of traffic.
    
    Attributes:
        lane_id: Unique identifier for the lane
        direction: Direction of traffic flow in this lane
        positions: Set of (row, col) positions that belong to this lane
        cars: List of cars currently in this lane
        max_cars: Maximum number of cars this lane can hold
    """
    
    def __init__(self, lane_id: str, direction: Direction, positions: Set[Tuple[int, int]]):
        self.lane_id = lane_id
        self.direction = direction
        self.positions = positions
        self.cars: List[Car] = []
        self.max_cars = len(positions)  # One car per position
    
    def add_car(self, car: Car) -> bool:
        """
        Add a car to this lane.
        
        Args:
            car: Car to add
            
        Returns:
            True if car was added successfully, False if lane is full
        """
        if len(self.cars) < self.max_cars and car.position in self.positions:
            self.cars.append(car)
            return True
        return False
    
    def remove_car(self, car: Car) -> bool:
        """
        Remove a car from this lane.
        
        Args:
            car: Car to remove
            
        Returns:
            True if car was removed, False if car not in lane
        """
        if car in self.cars:
            self.cars.remove(car)
            return True
        return False
    
    def get_car_at_position(self, position: Tuple[int, int]) -> Optional[Car]:
        """
        Get the car at a specific position.
        
        Args:
            position: The (row, col) position to check
            
        Returns:
            Car at that position, or None if no car there
        """
        for car in self.cars:
            if car.position == position:
                return car
        return None
    
    def is_position_free(self, position: Tuple[int, int]) -> bool:
        """
        Check if a position in this lane is free.
        
        Args:
            position: The (row, col) position to check
            
        Returns:
            True if position is free, False otherwise
        """
        return position in self.positions and self.get_car_at_position(position) is None


class Road:
    """
    Represents a road segment with multiple lanes.
    
    Attributes:
        road_id: Unique identifier for the road
        start_pos: Starting position of the road
        end_pos: Ending position of the road
        direction: Primary direction of the road
        lanes: Dictionary of lanes indexed by lane number
        num_lanes: Number of lanes in this road
    """
    
    def __init__(self, road_id: str, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                 direction: Direction, num_lanes: int = 2):
        self.road_id = road_id
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.direction = direction
        self.num_lanes = num_lanes
        self.lanes: Dict[int, Lane] = {}
        
        self._create_lanes()
    
    def _create_lanes(self) -> None:
        """Create lane objects for this road."""
        positions = self._get_road_positions()
        
        for lane_num in range(self.num_lanes):
            lane_positions = self._get_lane_positions(lane_num, positions)
            lane_id = f"{self.road_id}_lane_{lane_num}"
            self.lanes[lane_num] = Lane(lane_id, self.direction, lane_positions)
    
    def _get_road_positions(self) -> List[Tuple[int, int]]:
        """Get all positions that belong to this road."""
        positions = []
        start_row, start_col = self.start_pos
        end_row, end_col = self.end_pos
        
        if self.direction in [Direction.NORTH, Direction.SOUTH]:
            # Vertical road
            min_row, max_row = min(start_row, end_row), max(start_row, end_row)
            for row in range(min_row, max_row + 1):
                for lane_offset in range(self.num_lanes):
                    positions.append((row, start_col + lane_offset))
        else:
            # Horizontal road
            min_col, max_col = min(start_col, end_col), max(start_col, end_col)
            for col in range(min_col, max_col + 1):
                for lane_offset in range(self.num_lanes):
                    positions.append((start_row + lane_offset, col))
        
        return positions
    
    def _get_lane_positions(self, lane_num: int, all_positions: List[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Get positions for a specific lane."""
        lane_positions = set()
        
        if self.direction in [Direction.NORTH, Direction.SOUTH]:
            # For vertical roads, lanes are side by side
            for row, col in all_positions:
                if col == self.start_pos[1] + lane_num:
                    lane_positions.add((row, col))
        else:
            # For horizontal roads, lanes are stacked
            for row, col in all_positions:
                if row == self.start_pos[0] + lane_num:
                    lane_positions.add((row, col))
        
        return lane_positions
    
    def add_car(self, car: Car, lane_num: int = 0) -> bool:
        """
        Add a car to a specific lane.
        
        Args:
            car: Car to add
            lane_num: Lane number to add car to
            
        Returns:
            True if car was added successfully
        """
        if lane_num in self.lanes:
            success = self.lanes[lane_num].add_car(car)
            if success:
                car.lane = lane_num
            return success
        return False
    
    def remove_car(self, car: Car) -> bool:
        """Remove a car from this road."""
        for lane in self.lanes.values():
            if lane.remove_car(car):
                return True
        return False
    
    def get_all_cars(self) -> List[Car]:
        """Get all cars on this road."""
        all_cars = []
        for lane in self.lanes.values():
            all_cars.extend(lane.cars)
        return all_cars
    
    def is_position_free(self, position: Tuple[int, int], lane_num: Optional[int] = None) -> bool:
        """
        Check if a position is free.
        
        Args:
            position: Position to check
            lane_num: Specific lane to check, or None to check all lanes
            
        Returns:
            True if position is free
        """
        if lane_num is not None:
            if lane_num in self.lanes:
                return self.lanes[lane_num].is_position_free(position)
            return False
        
        # Check all lanes
        for lane in self.lanes.values():
            if position in lane.positions:
                return lane.is_position_free(position)
        return False
    
    def get_car_at_position(self, position: Tuple[int, int]) -> Optional[Car]:
        """Get car at a specific position."""
        for lane in self.lanes.values():
            car = lane.get_car_at_position(position)
            if car:
                return car
        return None
    
    def __str__(self) -> str:
        return f"Road({self.road_id}) {self.start_pos}->{self.end_pos} {self.direction.value} ({len(self.get_all_cars())} cars)"
