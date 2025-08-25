import random

traffic_queues = {
    "North": [],
    "South": [],
    "East": [],
    "West": []
}
signal_state = "NorthSouth"
simulation_time = 0
waiting_times_fixed = []
waiting_times_dynamic = []
fixed_green_duration = 5
signal_timer = 0

def get_queue_lengths():
    return {lane: len(queue) for lane, queue in traffic_queues.items()}

def simulate_car_arrivals():
    arrival_probability = {
        "North": 0.4,
        "South": 0.4,
        "East": 0.3,
        "West": 0.3
    }
    for lane, probability in arrival_probability.items():
        if random.random() < probability:
            traffic_queues[lane].append(("Car", simulation_time))

def run_simulation_step_fixed():
    global signal_state, signal_timer, simulation_time
    simulation_time += 1
    simulate_car_arrivals()
    signal_timer += 1
    if signal_timer >= fixed_green_duration:
        signal_state = "EastWest" if signal_state == "NorthSouth" else "NorthSouth"
        signal_timer = 0
    if signal_state == "NorthSouth":
        if traffic_queues["North"]:
            car, arrival_time = traffic_queues["North"].pop(0)
            waiting_times_fixed.append(simulation_time - arrival_time)
        if traffic_queues["South"]:
            car, arrival_time = traffic_queues["South"].pop(0)
            waiting_times_fixed.append(simulation_time - arrival_time)
    else:
        if traffic_queues["East"]:
            car, arrival_time = traffic_queues["East"].pop(0)
            waiting_times_fixed.append(simulation_time - arrival_time)
        if traffic_queues["West"]:
            car, arrival_time = traffic_queues["West"].pop(0)
            waiting_times_fixed.append(simulation_time - arrival_time)

def run_simulation_step_dynamic():
    global signal_state, simulation_time
    simulation_time += 1
    simulate_car_arrivals()
    queues = get_queue_lengths()
    if queues["North"] + queues["South"] > queues["East"] + queues["West"]:
        signal_state = "NorthSouth"
    else:
        signal_state = "EastWest"
    if signal_state == "NorthSouth":
        if traffic_queues["North"]:
            car, arrival_time = traffic_queues["North"].pop(0)
            waiting_times_dynamic.append(simulation_time - arrival_time)
        if traffic_queues["South"]:
            car, arrival_time = traffic_queues["South"].pop(0)
            waiting_times_dynamic.append(simulation_time - arrival_time)
    else:
        if traffic_queues["East"]:
            car, arrival_time = traffic_queues["East"].pop(0)
            waiting_times_dynamic.append(simulation_time - arrival_time)
        if traffic_queues["West"]:
            car, arrival_time = traffic_queues["West"].pop(0)
            waiting_times_dynamic.append(simulation_time - arrival_time)

def reset_simulation():
    global traffic_queues, signal_state, simulation_time, waiting_times_fixed, waiting_times_dynamic, signal_timer
    traffic_queues = {"North": [], "South": [], "East": [], "West": []}
    signal_state = "NorthSouth"
    simulation_time = 0
    waiting_times_fixed = []
    waiting_times_dynamic = []
    signal_timer = 0
    random.seed() 