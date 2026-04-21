import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Timeline from './pages/Timeline';
import Layout from './components/Layout';

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Restore user from local storage
    const storedUser = localStorage.getItem('smartdms_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const loginUser = (userData) => {
    setUser(userData);
    localStorage.setItem('smartdms_user', JSON.stringify(userData));
  };

  const logoutUser = () => {
    setUser(null);
    localStorage.removeItem('smartdms_user');
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login onLogin={loginUser} />} />
        <Route path="/signup" element={<Signup />} />
        
        {/* Protected Routes */}
        <Route path="/" element={user ? <Layout user={user} onLogout={logoutUser} /> : <Navigate to="/login" />}>
          <Route index element={<Dashboard user={user} />} />
          <Route path="upload" element={<Upload user={user} />} />
          <Route path="timeline" element={<Timeline user={user} />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
