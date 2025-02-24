import React from 'react';
import { Link } from 'react-router-dom'; 
import PropTypes from 'prop-types';
import { formatPrice } from '../utils/numberUtils';

/**
 * Alerts the user when their balance is low.
 *
 * @param {number} balance - The user's current balance.
 */
const LowBalanceWarning = ({ balance }) => {
    if (balance == null || balance > 1) return null;

    const isCritical = balance <= 0.05;
    const message = isCritical
        ? (
            <>
                ⛽ Your balance is critically low : ${formatPrice(balance)}. Please{' '}
                <Link to="/pricing">add funds</Link> to continue using The Thinker ⛽
            </>
        )
        : `⛽ Your balance is low : ${formatPrice(balance)}`;

    return (
      <div
        className={`low-balance-warning ${isCritical ? 'critical' : 'warning'}`}
        role="alert"
        aria-live="assertive"
      >
        {message}
      </div>
    );
};

LowBalanceWarning.propTypes = {
    balance: PropTypes.number.isRequired,
};

export default LowBalanceWarning;
