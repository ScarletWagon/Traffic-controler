# Traffic Simulation System

A comprehensive object-oriented backend for traffic simulation designed to support machine learning optimization of traffic light control.

## Features

- **Object-Oriented Design**: Clean separation of concerns with Car, Road, TrafficLight, and Intersection classes
- **Grid-Based Movement**: Block-based grid map with configurable car movement speeds
- **Traffic Light Control**: Support for Red, Yellow, Green, and Green Arrow states
- **ML Integration**: Exposes state information and allows external control of traffic lights
- **Scalable Architecture**: Designed to support multiple intersections and larger maps

## Classes

### Core Components

- `Car`: Tracks position, direction, intended movement, lane, and wait times
- `Road`: Manages multiple lanes with directional traffic flow
- `TrafficLight`: Individual light with state management
- `TrafficLightController`: Coordinates multiple lights at an intersection
- `Intersection`: Manages car flow through intersection with traffic light control
- `TrafficSimulation`: Main simulation engine coordinating all components

### Enums

- `Direction`: North, South, East, West
- `Movement`: Straight, Left, Right
- `TrafficLightState`: Red, Yellow, Green, Green Arrow
- `CellType`: Empty, Road, Intersection

## Usage

```python
from simulation import TrafficSimulation
from car import Car
from enums import Direction, Movement

# Create simulation
sim = TrafficSimulation(grid_size=(20, 20))

# Create a four-way intersection
intersection_id = sim.create_simple_four_way_intersection(center=(10, 10))

# Add cars
car = Car("car_001", (4, 10), Direction.SOUTH, Movement.STRAIGHT)
sim.add_car(car, "north_road", lane=0)

# Run simulation
for tick in range(10):
    sim.tick()
    state = sim.get_simulation_state()
    print(f"Tick {tick}: {state['total_cars']} cars, avg wait: {state['average_wait_time']:.1f}")

# ML Agent Control
sim.set_traffic_light(intersection_id, Direction.NORTH, TrafficLightState.GREEN)
```

## Machine Learning Integration

The system exposes comprehensive state information for ML agents:

- Car positions and wait times
- Traffic light states
- Intersection occupancy
- Average wait times for optimization

ML agents can control traffic lights by calling `set_traffic_light()` method.

## Running the Example

```bash
python example.py
```

This will demonstrate:
- Creating a four-way intersection
- Adding cars with different intended movements
- Automatic traffic light cycling
- ML agent control of lights
- Real-time simulation state monitoring

## Architecture Benefits

1. **Modularity**: Each component has clear responsibilities
2. **Extensibility**: Easy to add new intersection types or car behaviors
3. **ML Ready**: State observation and control interfaces built-in
4. **Performance**: Efficient position checking and car movement
5. **Realistic**: Respects traffic rules and physical constraints

## Future Enhancements

- Multiple intersection support
- More complex road networks
- Pedestrian crossings
- Emergency vehicle priority
- Advanced ML reward functions
