import React, { useState, useEffect } from "react";
import ReactDOM from 'react-dom/client';
import './index.css';
import App from "./App";
import reportWebVitals from './reportWebVitals';
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Settings, { SettingsProvider } from './pages/Settings/Settings';
import Pricing from './pages/Pricing/Pricing';
import Login from './pages/Login/Login';
import { apiFetch } from "./utils/authUtils";

import 'highlight.js/styles/atom-one-dark.css';

const flask_port = "http://localhost:5000";

function RootApp() {
  const [isAuthenticated, setIsAuthenticated] = useState(null);

  useEffect(() => {
    const validateSession = async () => {
      try {
        const response = await apiFetch(`${flask_port}/auth/validate`, {
            method: "GET",
            credentials: "include", // Include cookies in the request
        });

        setIsAuthenticated(response.ok);
      } catch (error) {
        console.error("Error validating session:", error);
        setIsAuthenticated(false);
      }
    };

    validateSession();
  }, []);

  if (isAuthenticated === null) {
    // Show a loading state while session is being validated
    return <div>Loading...</div>;
  }

  return (
    <SettingsProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          {/* Protected Routes */}
          <Route
            path="/"
            element={isAuthenticated ? <App /> : <Navigate to="/login" />}
          />
          <Route
            path="/settings"
            element={isAuthenticated ? <Settings /> : <Navigate to="/login" />}
          />
          <Route
            path="/pricing"
            element={isAuthenticated ? <Pricing /> : <Navigate to="/login" />}
          />
        </Routes>
      </BrowserRouter>
    </SettingsProvider>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<RootApp />);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();