# Smart Traffic Signal Simulator

A full-stack web application that simulates traffic signal behavior using Python Flask backend and React frontend.

## Project Structure

```
smart_traffic_simulator/
├── backend/
│   ├── traffic_sim.py      # Core simulation logic
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
└── frontend/
    └── traffic-ui/         # React application
        ├── public/
        │   └── index.html
        ├── src/
        │   ├── App.css
        │   ├── App.js
        │   ├── index.css
        │   └── index.js
        └── package.json
```

## Features

- **Fixed-Time Signal Simulation**: Traditional traffic signal with fixed timing cycles
- **Dynamic Signal Simulation**: Adaptive traffic signal that responds to queue lengths
- **Real-time Queue Monitoring**: Visual representation of vehicle queues in all directions
- **Performance Metrics**: Average waiting times and simulation statistics
- **Interactive Controls**: Step-by-step simulation with reset functionality

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd smart_traffic_simulator/backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flask server:
   ```bash
   python app.py
   ```

The backend will start on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd smart_traffic_simulator/frontend/traffic-ui
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

The frontend will start on `http://localhost:3000`

## Usage

1. **Choose Simulation Type**: Select between Fixed-Time or Dynamic signal modes
2. **Run Simulation**: Click "Simulate One Step" to advance the simulation
3. **Monitor Queues**: Watch vehicle queues build up in all four directions
4. **Track Performance**: View average waiting times and current signal state
5. **Reset**: Use the reset button to start over with fresh simulation data

## API Endpoints

- `GET /api/initial_state` - Get current simulation state
- `POST /api/simulate_step_fixed` - Run one step of fixed-time simulation
- `POST /api/simulate_step_dynamic` - Run one step of dynamic simulation
- `POST /api/reset` - Reset simulation to initial state

## Technical Details

- **Backend**: Python Flask with CORS support for cross-origin requests
- **Frontend**: React with hooks for state management
- **Communication**: RESTful API with JSON data exchange
- **Simulation**: Discrete-time simulation with probabilistic car arrivals
- **Signaling**: Two-phase traffic signal (North-South vs East-West)

## Dependencies

### Backend
- Flask
- Flask-CORS

### Frontend
- React 18
- Axios for HTTP requests
- React Scripts for development tools 