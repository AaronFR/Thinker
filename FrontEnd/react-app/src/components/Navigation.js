import React from 'react';
import { Link } from 'react-router-dom';
import './styles/Navigation.css';

const Navigation = () => {
  return (
    <nav>
      <Link to="/settings" className="link">Go to Settings</Link>
    </nav>
  );
};

export default Navigation;
