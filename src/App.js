import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from './app/Home';
import Auth from './app/Auth';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/auth" element={<Auth />} />
    </Routes>
  );
}

export default App;