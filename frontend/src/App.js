// src/App.js

import React, { useState } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [transactions, setTransactions] = useState([]);
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");

  const register = async () => {
    await axios.post(`${API_URL}/register/`, { username, password });
    alert("User registered successfully!");
  };

  const login = async () => {
    const response = await axios.post(`${API_URL}/token`, new URLSearchParams({
      username, password
    }));
    setToken(response.data.access_token);
  };

  const getTransactions = async () => {
    const response = await axios.get(`${API_URL}/transactions/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setTransactions(response.data.transactions);
  };

  const addTransaction = async () => {
    await axios.post(`${API_URL}/transactions/`, { description, amount }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    getTransactions();
  };

  return (
    <div className="App">
      <h1>Finance Tracker</h1>
      <div>
        <h2>Register</h2>
        <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button onClick={register}>Register</button>
      </div>

      <div>
        <h2>Login</h2>
        <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button onClick={login}>Login</button>
      </div>

      {token && (
        <div>
          <h2>Add Transaction</h2>
          <input placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
          <input placeholder="Amount" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
          <button onClick={addTransaction}>Add Transaction</button>

          <h2>Transactions</h2>
          <button onClick={getTransactions}>Get Transactions</button>
          <ul>
            {transactions.map((t, index) => (
              <li key={index}>{t.description}: ${t.amount}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
