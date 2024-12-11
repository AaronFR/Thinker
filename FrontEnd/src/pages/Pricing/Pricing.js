import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

import { apiFetch } from '../../utils/authUtils';
import TransactionForm from '../../components/TransactionForm';

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

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
    const [balance, setBalance] = useState(0.0);
    const [sessionCost, setSessionCost] = useState(0.0);

    const loadBalance = async () => {
        try {
            const response = await apiFetch(FLASK_PORT + '/pricing/balance', {
                method: 'GET',
                headers: {
                  "Content-Type": "application/json"
                },
                credentials: "include"
            });

            if (response.ok) {
                const balanceData = await response.json();
                if (balanceData && balanceData.balance) {
                    setBalance(balanceData.balance);
                }
            } else {
                console.error('Failed to load user balance', response);
            }
        } catch (error) {
            console.error('Error retrieving user balance:', error);
        }
    }

    const loadSessionCost = async () => {
        try {
            const response = await apiFetch(FLASK_PORT + '/pricing/session', {
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

    useEffect(() => {
        loadBalance();
        loadSessionCost();
    }, []);

    return (
        <div className="settings-container">
            <nav className="settings-nav">
                <Link to="/" className="link">Home</Link>
                <Link to="/settings" className="link">Settings</Link>
            </nav>

            <h2>Balance: {FormatPrice(balance)}</h2>
            <h3>Current session: {FormatPrice(sessionCost)}</h3>

            {/* Pass loadBalance as a prop to TransactionForm */}
            <TransactionForm onSuccess={loadBalance} />
        </div>
    );
}

export default Pricing;
