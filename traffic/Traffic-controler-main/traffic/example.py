"""
Example usage of the traffic simulation system.
Demonstrates creating a four-way intersection with cars and running simulation ticks.
"""
import random
from simulation import TrafficSimulation
from car import Car
from enums import Direction, Movement, TrafficLightState


def create_sample_cars(simulation: TrafficSimulation) -> None:
    """Create some sample cars for testing."""
    
    # Car 1: On north road, going straight through intersection
    car1 = Car("car_001", (4, 10), Direction.SOUTH, Movement.STRAIGHT, lane=0)
    simulation.add_car(car1, "north_road", 0)
    
    # Car 2: On north road, wants to turn left
    car2 = Car("car_002", (6, 10), Direction.SOUTH, Movement.LEFT, lane=1)
    simulation.add_car(car2, "north_road", 1)
    
    # Car 3: On east road, going straight
    car3 = Car("car_003", (10, 12), Direction.WEST, Movement.STRAIGHT, lane=0)
    simulation.add_car(car3, "east_road", 0)
    
    # Car 4: On west road, wants to turn right
    car4 = Car("car_004", (10, 8), Direction.EAST, Movement.RIGHT, lane=0)
    simulation.add_car(car4, "west_road", 0)
    
    # Car 5: On south road, going straight
    car5 = Car("car_005", (14, 10), Direction.NORTH, Movement.STRAIGHT, lane=0)
    simulation.add_car(car5, "south_road", 0)


def print_simulation_state(simulation: TrafficSimulation) -> None:
    """Print current state of the simulation."""
    print(f"\n--- Simulation Tick {simulation.tick_count} ---")
    
    # Print car positions and states
    print("Cars:")
    for car in simulation.cars:
        road_id, intersection_id = simulation.find_car_location(car)
        location = road_id if road_id else f"intersection:{intersection_id}"
        print(f"  {car.car_id}: {car.position} -> {car.direction.value} "
              f"(wants to {car.intended_movement.value}) wait:{car.wait_time} at {location}")
    
    # Print traffic light states
    print("\nTraffic Lights:")
    for intersection_id, intersection in simulation.intersections.items():
        lights = intersection.traffic_controller.get_state_info()
        print(f"  {intersection_id}:")
        for direction, state in lights.items():
            print(f"    {direction.value}: {state.value}")
    
    # Print summary statistics
    state = simulation.get_simulation_state()
    print(f"\nStats: {state['total_cars']} cars, avg wait: {state['average_wait_time']:.1f}")


def demonstrate_ml_control(simulation: TrafficSimulation) -> None:
    """Demonstrate ML agent control of traffic lights."""
    print("\n=== Demonstrating ML Agent Control ===")
    
    # ML agent decides to give green light to north-south traffic
    intersection_id = "main_intersection"
    
    print("ML Agent: Setting North-South lights to GREEN")
    simulation.set_traffic_light(intersection_id, Direction.NORTH, TrafficLightState.GREEN)
    simulation.set_traffic_light(intersection_id, Direction.SOUTH, TrafficLightState.GREEN)
    simulation.set_traffic_light(intersection_id, Direction.EAST, TrafficLightState.RED)
    simulation.set_traffic_light(intersection_id, Direction.WEST, TrafficLightState.RED)
    
    # Run a few ticks
    for i in range(3):
        simulation.tick()
        print_simulation_state(simulation)
    
    print("\nML Agent: Setting East-West lights to GREEN")
    simulation.set_traffic_light(intersection_id, Direction.NORTH, TrafficLightState.RED)
    simulation.set_traffic_light(intersection_id, Direction.SOUTH, TrafficLightState.RED)
    simulation.set_traffic_light(intersection_id, Direction.EAST, TrafficLightState.GREEN)
    simulation.set_traffic_light(intersection_id, Direction.WEST, TrafficLightState.GREEN)
    
    # Run a few more ticks
    for i in range(3):
        simulation.tick()
        print_simulation_state(simulation)


def main():
    """Main demonstration function."""
    print("Traffic Simulation System Demo")
    print("=============================")
    
    # Create simulation
    simulation = TrafficSimulation(grid_size=(20, 20))
    
    # Create a four-way intersection
    intersection_id = simulation.create_simple_four_way_intersection(center=(10, 10))
    print(f"Created intersection: {intersection_id}")
    
    # Add some cars
    create_sample_cars(simulation)
    print(f"Added {len(simulation.cars)} cars to the simulation")
    
    # Print initial state
    print_simulation_state(simulation)
    
    print("\n=== Running Automatic Traffic Light Cycle ===")
    
    # Run simulation for several ticks with automatic traffic light control
    for tick in range(5):
        simulation.tick()
        print_simulation_state(simulation)
        
        # Add some randomness - occasionally add a new car
        if random.random() < 0.3:  # 30% chance
            road_choices = ["north_road", "south_road", "east_road", "west_road"]
            direction_choices = [Direction.SOUTH, Direction.NORTH, Direction.WEST, Direction.EAST]
            movement_choices = [Movement.STRAIGHT, Movement.LEFT, Movement.RIGHT]
            
            road_id = random.choice(road_choices)
            idx = road_choices.index(road_id)
            direction = direction_choices[idx]
            
            # Find a suitable starting position
            road = simulation.roads[road_id]
            start_positions = list(road.lanes[0].positions)
            if start_positions:
                start_pos = random.choice(start_positions)
                if simulation.is_position_free(start_pos):
                    new_car = Car(
                        f"car_{random.randint(100, 999)}",
                        start_pos,
                        direction,
                        random.choice(movement_choices)
                    )
                    if simulation.add_car(new_car, road_id, 0):
                        print(f"  -> Added new car: {new_car.car_id}")
    
    # Demonstrate ML control
    demonstrate_ml_control(simulation)
    
    # Print final simulation state
    final_state = simulation.get_simulation_state()
    print(f"\n=== Final Simulation State ===")
    print(f"Total ticks: {final_state['tick']}")
    print(f"Total cars: {final_state['total_cars']}")
    print(f"Average wait time: {final_state['average_wait_time']:.2f}")
    
    print(f"\nCar wait times:")
    for car_id, wait_time in final_state['car_wait_times'].items():
        print(f"  {car_id}: {wait_time} ticks")


if __name__ == "__main__":
    # Set random seed for reproducible results
    random.seed(42)
    main()
