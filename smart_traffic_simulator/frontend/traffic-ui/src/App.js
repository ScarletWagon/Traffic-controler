// frontend/src/App.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [queues, setQueues] = useState({ North: 0, South: 0, East: 0, West: 0 });
  const [signalState, setSignalState] = useState('NorthSouth');
  const [simulationTime, setSimulationTime] = useState(0);
  const [simulationType, setSimulationType] = useState('fixed');
  const [waitingTimes, setWaitingTimes] = useState([]);

  useEffect(() => {
    fetchInitialState();
  }, []);

  const fetchInitialState = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/initial_state`);
      const { queues, signalState, simulationTime, waitingTimesFixed, waitingTimesDynamic } = response.data;
      setQueues(queues);
      setSignalState(signalState);
      setSimulationTime(simulationTime);
      setWaitingTimes(simulationType === 'fixed' ? waitingTimesFixed : waitingTimesDynamic);
    } catch (error) {
      console.error('Error fetching initial state:', error);
    }
  };

  const handleSimulateStep = async () => {
    try {
      const endpoint = simulationType === 'fixed'
        ? `${API_BASE_URL}/simulate_step_fixed`
        : `${API_BASE_URL}/simulate_step_dynamic`;

      const response = await axios.post(endpoint);
      const { queues, signalState, simulationTime, waitingTimesFixed, waitingTimesDynamic } = response.data;
      setQueues(queues);
      setSignalState(signalState);
      setSimulationTime(simulationTime);
      if (simulationType === 'fixed') {
        setWaitingTimes(waitingTimesFixed);
      } else {
        setWaitingTimes(waitingTimesDynamic);
      }
    } catch (error) {
      console.error('Error simulating step:', error);
    }
  };

  const handleReset = async () => {
    try {
      await axios.post(`${API_BASE_URL}/reset`);
      fetchInitialState();
    } catch (error) {
      console.error('Error resetting simulation:', error);
    }
  };

  const calculateAverageWaitTime = () => {
    if (waitingTimes.length === 0) return 0;
    const sum = waitingTimes.reduce((acc, time) => acc + time, 0);
    return (sum / waitingTimes.length).toFixed(2);
  };

  return (
    <div className="app-container">
      <h1>Smart Traffic Signal Simulator</h1>
      <div className="controls">
        <button onClick={() => { setSimulationType('fixed'); handleReset(); }}>Fixed-Time Signal</button>
        <button onClick={() => { setSimulationType('dynamic'); handleReset(); }}>Dynamic Signal</button>
        <button onClick={handleSimulateStep}>Simulate One Step</button>
        <button onClick={handleReset}>Reset</button>
      </div>
      <div className="simulation-data">
        <div className="data-box">
          <p>Simulation Time: <span>{simulationTime}</span></p>
        </div>
        <div className="data-box">
          <p>Current Signal: <span>{signalState}</span></p>
        </div>
        <div className="data-box">
          <p>Average Wait Time: <span>{calculateAverageWaitTime()}</span></p>
        </div>
      </div>
      <div className="intersection-container">
        <div className="queue north-queue">North Queue: {queues.North}</div>
        <div className="queue south-queue">South Queue: {queues.South}</div>
        <div className="queue east-queue">East Queue: {queues.East}</div>
        <div className="queue west-queue">West Queue: {queues.West}</div>
      </div>
    </div>
  );
}

export default App; 