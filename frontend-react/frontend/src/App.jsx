import React from 'react';
import Login from './components/login';
import Register from './components/register';
import UserPage from './components/user_page';
import { BrowserRouter as Router, Routes, Route, Link, Navigate} from "react-router-dom"
//import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/login" />}/>
          <Route path="/login" element={<Login/>}/>
          <Route path="/register" element={<Register/>}/>
          <Route path="/user_page" element={<UserPage/>}/>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
