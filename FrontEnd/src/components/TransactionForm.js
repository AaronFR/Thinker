import React, { useState } from 'react';
import PropTypes from 'prop-types';

import { apiFetch } from '../utils/authUtils';
import './styles/TransactionForm.css';

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

/**
 * TransactionForm Component
 * 
 * Renders a form that allows users to top up their balance.
 * Validates user input, handles form submission, and provides real-time feedback.
 *
 * @param onSuccess: Callback function invoked upon successful transaction.
 */
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

    /**
     * Attempts to process the transaction.
     *
     * @param {Event} event - The form submission event.
     */
    const attemptTransaction = async (event) => {
        event.preventDefault();
        setError('');
        setSuccess('');

        if (!validateAmount(amount)) {
            setError('Please enter a valid positive amount.');
            return;
        }

        setIsLoading(true);

        try {
            const floatAmount = parseFloat(amount).toFixed(2); // only dollars and cents ($)1.23456 -> ($)1.23

            const response = await apiFetch(`${FLASK_PORT}/pricing/add`, {
                method: 'POST',
                body: JSON.stringify({ sum: parseFloat(floatAmount) }),
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
     * @param {Event} e - The input change event.
     */
    const handleAmountChange = (e) => {
        const value = e.target.value;
        if (/^\d*\.?\d{0,2}$/.test(value)) {
            setAmount(value);
            if (error) setError('');
        }
    };

    return (
        <form onSubmit={attemptTransaction} aria-label="Transaction Form">
            <h3>Top Up Your Balance $</h3>
            <div className="form-group">
                <label htmlFor="amount" className="visually-hidden">
                    Amount in dollars
                </label>
                <input
                    type="text"
                    className={`input-field ${error ? 'input-error' : ''}`}
                    id="amount"
                    name="amount"
                    placeholder='Amount in dollars $...'
                    value={amount}
                    onChange={handleAmountChange}
                    aria-describedby="amountHelp"
                    required
                    aria-invalid={!!error}
                />
                <small id="amountHelp" className="form-text">
                    Enter the amount in USD (e.g., 5.00)
                </small>
                {error && <p className="error-message" role="alert">{error}</p>}
                {success && <p className="success-message" role="status">{success}</p>}
            </div>
            <button
                type="submit"
                disabled={isLoading}
                className={`submit-button ${isLoading ? 'button-loading' : ''}`}
                aria-busy={isLoading}
            >
                {isLoading ? 'Processing...' : 'Pay'}
            </button>
        </form>
    );
};

TransactionForm.propTypes = {
    onSuccess: PropTypes.func.isRequired,
};

export default TransactionForm;
