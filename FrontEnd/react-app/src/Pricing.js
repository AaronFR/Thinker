import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';


const flask_port= "http://localhost:5000"

export function Pricing() {
    const [sessionCost, setSessionCost] = useState(0.0)

    useEffect(() => {
        const loadCosts = async () => {
            console.log("retrieving session costs")
            const response = await fetch(flask_port + '/pricing/session', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            })

            if (response.ok) {
                const priceData = await response.json();
                console.log(priceData)
                if (priceData && priceData.cost) {
                    setSessionCost(priceData.cost)
                }
            } else {
                console.error('Failed to load session price');
            }
        }
        loadCosts();
    }, [])

    return (
      <div>
        <nav>
          <Link to="/" className="link">Home</Link>
          <Link to="/settings" className="link">Settings</Link>
        </nav>
        
  
        <h2>Session cost: ${sessionCost}</h2>
      </div>
    );
  }
  
  export default Pricing;