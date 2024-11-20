import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';


const flask_port= "http://localhost:5000"

function FormatPrice(price) {
    const scale = 100
    if (price < 1) {
        const cents = Math.round(price * 100 * scale) / scale
        return `¢ ${cents}`;
    } else {
        const roundedPrice = parseFloat(price.toPrecision(4))
        return `$${roundedPrice}`;
    }
}

export function Pricing() {
    const [sessionCost, setSessionCost] = useState(0.0)

    useEffect(() => {
        const loadSessionCost  = async () => {
            try {
                const response = await fetch(flask_port + '/pricing/session', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: "include",
                });

                if (response.ok) {
                    const priceData = await response.json();
                    if (priceData && priceData.cost) {
                        setSessionCost(priceData.cost);
                    }
                } else {
                    console.error('Failed to load session price');
                }
            } catch (error) {
                console.error('Error retrieving session cost:', error);
            }
        };
        
        loadSessionCost();
    }, []);

    return (
      <div className="settings-container">
        <nav className="settings-nav">
          <Link to="/" className="link">Home</Link>
          <Link to="/settings" className="link">Settings</Link>
        </nav>
        
        <h2>Session cost: {FormatPrice(sessionCost)}</h2>
      </div>
    );
  }
  
  export default Pricing;