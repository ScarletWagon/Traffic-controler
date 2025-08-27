"""
Traffic light class for traffic simulation.
"""
from typing import Dict
from enums import Direction, TrafficLightState


class TrafficLight:
    """
    Represents a traffic light controlling one direction of an intersection.
    
    Attributes:
        light_id: Unique identifier for the traffic light
        direction: Which direction this light controls
        state: Current state of the light
        timer: Time remaining in current state
    """
    
    def __init__(self, light_id: str, direction: Direction, initial_state: TrafficLightState = TrafficLightState.RED):
        self.light_id = light_id
        self.direction = direction
        self.state = initial_state
        self.timer = 0
    
    def set_state(self, new_state: TrafficLightState, duration: int = 0) -> None:
        """
        Set the traffic light to a new state.
        
        Args:
            new_state: The new state for the light
            duration: How long to stay in this state (0 = indefinite)
        """
        self.state = new_state
        self.timer = duration
    
    def update(self) -> None:
        """Update the traffic light (decrement timer if active)."""
        if self.timer > 0:
            self.timer -= 1
    
    def can_go_straight(self) -> bool:
        """Check if cars can go straight through this light."""
        return self.state in [TrafficLightState.GREEN, TrafficLightState.GREEN_ARROW]
    
    def can_turn_left(self) -> bool:
        """Check if cars can turn left through this light."""
        return self.state == TrafficLightState.GREEN_ARROW
    
    def can_turn_right(self) -> bool:
        """Check if cars can turn right (typically always allowed unless red)."""
        return self.state != TrafficLightState.RED
    
    def __str__(self) -> str:
        return f"TrafficLight({self.light_id}) {self.direction.value}: {self.state.value}"
    
    def __repr__(self) -> str:
        return self.__str__()


class TrafficLightController:
    """
    Controls multiple traffic lights at an intersection.
    Provides coordinated control and state management.
    """
    
    def __init__(self, intersection_id: str):
        self.intersection_id = intersection_id
        self.lights: Dict[Direction, TrafficLight] = {}
        self.cycle_position = 0
        self.cycle_timer = 0
        
        # Default cycle: North-South green, then East-West green
        self.default_cycle = [
            (Direction.NORTH, Direction.SOUTH),  # North-South gets green
            (Direction.EAST, Direction.WEST)     # East-West gets green
        ]
        self.cycle_duration = 30  # ticks per cycle phase
    
    def add_light(self, direction: Direction) -> TrafficLight:
        """
        Add a traffic light for a specific direction.
        
        Args:
            direction: The direction this light controls
            
        Returns:
            The created TrafficLight instance
        """
        light_id = f"{self.intersection_id}_{direction.value}"
        light = TrafficLight(light_id, direction)
        self.lights[direction] = light
        return light
    
    def set_light_state(self, direction: Direction, state: TrafficLightState) -> None:
        """
        Set a specific light's state (for ML agent control).
        
        Args:
            direction: Which light to control
            state: New state for the light
        """
        if direction in self.lights:
            self.lights[direction].set_state(state)
    
    def update_automatic_cycle(self) -> None:
        """Update lights based on automatic cycling."""
        self.cycle_timer += 1
        
        if self.cycle_timer >= self.cycle_duration:
            self.cycle_timer = 0
            self.cycle_position = (self.cycle_position + 1) % len(self.default_cycle)
        
        # Set all lights to red first
        for light in self.lights.values():
            light.set_state(TrafficLightState.RED)
        
        # Set current cycle directions to green
        green_directions = self.default_cycle[self.cycle_position]
        for direction in green_directions:
            if direction in self.lights:
                self.lights[direction].set_state(TrafficLightState.GREEN)
    
    def update(self) -> None:
        """Update all traffic lights."""
        for light in self.lights.values():
            light.update()
    
    def get_state_info(self) -> Dict[Direction, TrafficLightState]:
        """Get current state of all lights (for ML observation)."""
        return {direction: light.state for direction, light in self.lights.items()}
    
    def __str__(self) -> str:
        light_states = ", ".join([f"{d.value}: {l.state.value}" for d, l in self.lights.items()])
        return f"TrafficLightController({self.intersection_id}) [{light_states}]"
