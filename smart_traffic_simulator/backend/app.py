from flask import Flask, jsonify, request
from flask_cors import CORS
import time


from traffic_sim import (
    traffic_queues,
    signal_state,
    simulation_time,
    waiting_times_fixed,
    waiting_times_dynamic,
    run_simulation_step_fixed,
    run_simulation_step_dynamic,
    reset_simulation,
    get_queue_lengths
)

app = Flask(__name__)
CORS(app)

@app.route('/api/initial_state', methods=['GET'])
def get_initial_state():
    return jsonify({
        'queues': get_queue_lengths(),
        'signalState': signal_state,
        'simulationTime': simulation_time,
        'waitingTimesFixed': waiting_times_fixed,
        'waitingTimesDynamic': waiting_times_dynamic,
    })

@app.route('/api/simulate_step_fixed', methods=['POST'])
def simulate_step_fixed():
    run_simulation_step_fixed()
    return jsonify({
        'queues': get_queue_lengths(),
        'signalState': signal_state,
        'simulationTime': simulation_time,
        'waitingTimesFixed': waiting_times_fixed[:]
    })

@app.route('/api/simulate_step_dynamic', methods=['POST'])
def simulate_step_dynamic():
    run_simulation_step_dynamic()
    return jsonify({
        'queues': get_queue_lengths(),
        'signalState': signal_state,
        'simulationTime': simulation_time,
        'waitingTimesDynamic': waiting_times_dynamic[:]
    })

@app.route('/api/reset', methods=['POST'])
def reset_all_data():
    reset_simulation()
    return jsonify({'message': 'Simulation reset'})

if __name__ == '__main__':
    app.run(debug=True) 