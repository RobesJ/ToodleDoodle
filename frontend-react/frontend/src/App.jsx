import React from 'react';
import Login from './components/login';
import Register from './components/register';
import { BrowserRouter as Router, Routes, Route, Link, Navigate} from "react-router-dom"
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/login" />}/>
          <Route path="/login" element={<Login/>}/>
          <Route path="/register" element={<Register/>}/>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
