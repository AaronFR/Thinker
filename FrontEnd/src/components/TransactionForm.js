import React, { useState } from 'react';
import { apiFetch } from '../utils/authUtils';

const FLASK_PORT = "http://localhost:5000"

const TransactionForm = ({ onSuccess }) => {
    const [amount, setAmount] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    /**
     * Validates the input to ensure it is a positive float with up to two decimal places.
     *
     * @param {string} value - The input value to validate.
     * @returns {boolean} - Returns true if valid, else false.
     */
    const validateAmount = (value) => {
        const floatValue = parseFloat(value);
        const regex = /^\d+(\.\d{1,2})?$/; // Two decimal places allowed
        return !isNaN(floatValue) && floatValue > 0 && regex.test(value);
    };

    const attemptTransaction = async (event) => {
        event.preventDefault();
        setError('');
        setSuccess('');

        if (!validateAmount(amount)) {
            setError('Please enter a valid positive amount.');
            return;
        }

        setIsLoading(true);
        console.log("Transaction attempted with amount: $", amount);

        try {
            const floatAmount = parseFloat(amount).toFixed(2); // only dollars and cents ($)1.23456 -> ($)1.23

            const response = await apiFetch(`${FLASK_PORT}/pricing/add`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ sum: parseFloat(floatAmount) }),
                credentials: "include"
            });

            if (!response.ok) {
                throw new Error('Failed to update your balance');
            }

            setSuccess('Your balance has been successfully updated.');
            setAmount('');

            // Call onSuccess to refresh the balance
            onSuccess();
        } catch (error) {
            console.error('Error topping up user balance:', error);
            setError('There was an issue processing your transaction. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    /**
     * Handles changes to accept only whole dollars and cents as a float
     *
     * @param {Event} e - The event object.
     */
    const handleAmountChange = (e) => {
        const value = e.target.value;
        if (/^\d*\.?\d{0,2}$/.test(value)) {
            setAmount(value);
        }
    };

    return (
        <form onSubmit={attemptTransaction}>
            <h3>Top up $</h3>
            <label htmlFor="amount" className="visually-hidden">Amount in dollars</label>
            <input
                type="text"
                id="amount"
                name="amount"
                placeholder='Amount in dollars $...'
                value={amount}
                onChange={handleAmountChange}
                aria-describedby="amountHelp"
                required
            />
            {error && <p className="error-message" role="alert">{error}</p>}
            {success && <p className="success-message" role="status">{success}</p>}
            <button type="submit" disabled={isLoading}>
                {isLoading ? 'Processing...' : 'Pay'}
            </button>
        </form>
    );
};

export default TransactionForm;
