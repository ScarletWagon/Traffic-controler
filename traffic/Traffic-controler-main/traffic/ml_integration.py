"""
Advanced ML integration example for the traffic simulation system.
Demonstrates how to create custom reward functions and state observations for reinforcement learning.
"""
import numpy as np
from typing import Dict, List, Tuple, Any
from simulation import TrafficSimulation
from car import Car
from enums import Direction, Movement, TrafficLightState


class MLTrafficAgent:
    """
    Example ML agent that can observe the simulation state and control traffic lights.
    This demonstrates the interface that a reinforcement learning agent would use.
    """
    
    def __init__(self, simulation: TrafficSimulation):
        self.simulation = simulation
        self.observation_history: List[Dict] = []
        self.action_history: List[Dict] = []
        
    def get_state_vector(self) -> np.ndarray:
        """
        Convert simulation state to a feature vector for ML models.
        
        Returns:
            Numpy array representing the current state
        """
        state = self.simulation.get_simulation_state()
        
        # Basic features
        features = [
            state['total_cars'],
            state['average_wait_time'],
            self.simulation.tick_count
        ]
        
        # Traffic light states (one-hot encoded)
        for intersection_id, intersection_data in state['intersections'].items():
            lights = intersection_data['traffic_lights']
            for direction in [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]:
                if direction in lights:
                    light_state = lights[direction]
                    # One-hot encode: [red, yellow, green, green_arrow]
                    features.extend([
                        1 if light_state == TrafficLightState.RED else 0,
                        1 if light_state == TrafficLightState.YELLOW else 0,
                        1 if light_state == TrafficLightState.GREEN else 0,
                        1 if light_state == TrafficLightState.GREEN_ARROW else 0
                    ])
                else:
                    features.extend([0, 0, 0, 0])  # No light
        
        # Car positions and wait times (aggregated by road/intersection)
        road_car_counts = {}
        road_wait_times = {}
        
        for car in self.simulation.cars:
            road_id, intersection_id = self.simulation.find_car_location(car)
            location = road_id if road_id else f"intersection_{intersection_id}"
            
            if location not in road_car_counts:
                road_car_counts[location] = 0
                road_wait_times[location] = []
            
            road_car_counts[location] += 1
            road_wait_times[location].append(car.wait_time)
        
        # Add road-specific features
        for road_name in ["north_road", "south_road", "east_road", "west_road"]:
            features.extend([
                road_car_counts.get(road_name, 0),
                np.mean(road_wait_times.get(road_name, [0])),
                len(road_wait_times.get(road_name, []))
            ])
        
        # Intersection occupancy
        for intersection_id, intersection_data in state['intersections'].items():
            features.append(intersection_data['cars_count'])
        
        return np.array(features, dtype=np.float32)
    
    def calculate_reward(self, previous_state: Dict, current_state: Dict) -> float:
        """
        Calculate reward for reinforcement learning based on simulation performance.
        
        Args:
            previous_state: Previous simulation state
            current_state: Current simulation state
            
        Returns:
            Reward value (higher is better)
        """
        # Primary objective: minimize average wait time
        prev_wait = previous_state.get('average_wait_time', 0)
        curr_wait = current_state.get('average_wait_time', 0)
        wait_improvement = prev_wait - curr_wait
        
        # Secondary objective: maximize throughput (cars moving)
        prev_total = previous_state.get('total_cars', 0)
        curr_total = current_state.get('total_cars', 0)
        
        # Count cars that have moved (approximation)
        cars_moved = max(0, prev_total - curr_total)
        
        # Penalty for cars waiting too long
        long_wait_penalty = 0
        for wait_time in current_state.get('car_wait_times', {}).values():
            if wait_time > 10:  # Arbitrary threshold
                long_wait_penalty += (wait_time - 10) * 0.1
        
        # Combine rewards
        reward = (
            wait_improvement * 10.0 +  # Weight wait time improvement heavily
            cars_moved * 5.0 +         # Reward throughput
            -long_wait_penalty         # Penalize long waits
        )
        
        return reward
    
    def choose_action(self, state_vector: np.ndarray) -> Dict[str, Any]:
        """
        Choose an action based on the current state.
        This is a simple rule-based policy - replace with ML model.
        
        Args:
            state_vector: Current state features
            
        Returns:
            Action dictionary specifying traffic light changes
        """
        # Simple rule-based policy for demonstration
        # In practice, this would be replaced by a neural network or other ML model
        
        action = {}
        
        # Get current state
        sim_state = self.simulation.get_simulation_state()
        
        # Find intersection with highest average wait time
        max_wait_intersection = None
        max_wait_time = 0
        
        for intersection_id, intersection_data in sim_state['intersections'].items():
            # Calculate average wait time for cars approaching this intersection
            approaching_wait = 0
            approaching_count = 0
            
            for car in self.simulation.cars:
                road_id, _ = self.simulation.find_car_location(car)
                if road_id and car.wait_time > 0:
                    approaching_wait += car.wait_time
                    approaching_count += 1
            
            if approaching_count > 0:
                avg_wait = approaching_wait / approaching_count
                if avg_wait > max_wait_time:
                    max_wait_time = avg_wait
                    max_wait_intersection = intersection_id
        
        # Set lights to help cars with high wait times
        if max_wait_intersection and max_wait_time > 3:
            # Determine which direction has the most waiting cars
            road_priorities = {
                "north_road": (Direction.NORTH, 0),
                "south_road": (Direction.SOUTH, 0),
                "east_road": (Direction.EAST, 0),
                "west_road": (Direction.WEST, 0)
            }
            
            for car in self.simulation.cars:
                road_id, _ = self.simulation.find_car_location(car)
                if road_id in road_priorities and car.wait_time > 0:
                    direction, count = road_priorities[road_id]
                    road_priorities[road_id] = (direction, count + car.wait_time)
            
            # Find direction with highest total wait time
            best_direction = max(road_priorities.values(), key=lambda x: x[1])[0]
            
            action[max_wait_intersection] = {
                best_direction: TrafficLightState.GREEN,
                # Set perpendicular directions to red
            }
            
            # Set perpendicular directions to red
            if best_direction in [Direction.NORTH, Direction.SOUTH]:
                action[max_wait_intersection][Direction.EAST] = TrafficLightState.RED
                action[max_wait_intersection][Direction.WEST] = TrafficLightState.RED
            else:
                action[max_wait_intersection][Direction.NORTH] = TrafficLightState.RED
                action[max_wait_intersection][Direction.SOUTH] = TrafficLightState.RED
        
        return action
    
    def step(self) -> Tuple[np.ndarray, float, Dict]:
        """
        Perform one ML agent step: observe, act, get reward.
        
        Returns:
            Tuple of (state_vector, reward, info)
        """
        # Get previous state
        prev_state = self.simulation.get_simulation_state()
        
        # Get current observation
        state_vector = self.get_state_vector()
        
        # Choose and execute action
        action = self.choose_action(state_vector)
        
        # Apply actions to simulation
        for intersection_id, light_changes in action.items():
            for direction, state in light_changes.items():
                self.simulation.set_traffic_light(intersection_id, direction, state)
        
        # Step simulation
        self.simulation.tick()
        
        # Get new state and calculate reward
        new_state = self.simulation.get_simulation_state()
        reward = self.calculate_reward(prev_state, new_state)
        
        # Store history
        self.observation_history.append(prev_state)
        self.action_history.append(action)
        
        # Return info for logging/debugging
        info = {
            'action_taken': action,
            'reward': reward,
            'cars_waiting': sum(1 for car in self.simulation.cars if car.wait_time > 0),
            'avg_wait_time': new_state['average_wait_time']
        }
        
        return state_vector, reward, info


def demonstrate_ml_agent():
    """Demonstrate the ML agent in action."""
    print("=== ML Agent Training Demonstration ===\n")
    
    # Create simulation
    simulation = TrafficSimulation(grid_size=(20, 20))
    intersection_id = simulation.create_simple_four_way_intersection(center=(10, 10))
    
    # Create ML agent
    agent = MLTrafficAgent(simulation)
    
    # Add initial cars
    cars_data = [
        ("car_001", (4, 10), Direction.SOUTH, Movement.STRAIGHT, "north_road"),
        ("car_002", (6, 10), Direction.SOUTH, Movement.LEFT, "north_road"),
        ("car_003", (10, 12), Direction.WEST, Movement.STRAIGHT, "east_road"),
        ("car_004", (10, 8), Direction.EAST, Movement.RIGHT, "west_road"),
        ("car_005", (14, 10), Direction.NORTH, Movement.STRAIGHT, "south_road"),
    ]
    
    for car_id, pos, direction, movement, road_id in cars_data:
        car = Car(car_id, pos, direction, movement)
        simulation.add_car(car, road_id, 0)
    
    print(f"Created simulation with {len(simulation.cars)} cars")
    print(f"Initial state vector shape: {agent.get_state_vector().shape}")
    
    # Run ML agent for several steps
    total_reward = 0
    
    for step in range(15):
        state_vector, reward, info = agent.step()
        total_reward += reward
        
        print(f"\nStep {step + 1}:")
        print(f"  Reward: {reward:.2f}")
        print(f"  Cars waiting: {info['cars_waiting']}")
        print(f"  Avg wait time: {info['avg_wait_time']:.2f}")
        print(f"  Action: {info['action_taken']}")
        
        # Add some new cars occasionally
        if step % 5 == 0 and step > 0:
            import random
            road_choices = ["north_road", "south_road", "east_road", "west_road"]
            direction_choices = [Direction.SOUTH, Direction.NORTH, Direction.WEST, Direction.EAST]
            
            road_id = random.choice(road_choices)
            idx = road_choices.index(road_id)
            direction = direction_choices[idx]
            
            road = simulation.roads[road_id]
            start_positions = list(road.lanes[0].positions)
            if start_positions:
                start_pos = random.choice(start_positions)
                if simulation.is_position_free(start_pos):
                    new_car = Car(
                        f"car_{step}_new",
                        start_pos,
                        direction,
                        random.choice([Movement.STRAIGHT, Movement.LEFT, Movement.RIGHT])
                    )
                    if simulation.add_car(new_car, road_id, 0):
                        print(f"  -> Added new car: {new_car.car_id}")
    
    print(f"\n=== Training Results ===")
    print(f"Total reward: {total_reward:.2f}")
    print(f"Average reward per step: {total_reward / 15:.2f}")
    print(f"Final cars in simulation: {len(simulation.cars)}")
    
    final_state = simulation.get_simulation_state()
    print(f"Final average wait time: {final_state['average_wait_time']:.2f}")


if __name__ == "__main__":
    # Set random seed for reproducible results
    import random
    random.seed(123)
    
    demonstrate_ml_agent()
