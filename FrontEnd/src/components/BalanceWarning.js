import React from 'react';
import PropTypes from 'prop-types';

/**
 * LowBalanceWarning component alerts the user when balance is low.
 *
 * @param {number} balance - The user's current balance.
 */
const LowBalanceWarning = ({ balance }) => {
    if (balance == null || balance > 1) return null;

    return (
      <div className="low-balance-warning">
        {balance > 0.05 ? (
          <span>
            ⛽ Your balance is low (${balance})
          </span>
        ) : (
          <span>
            ⛽ Your balance is low (${balance}). Please add funds to continue using The Thinker ⛽
          </span>
        )}
      </div>
    );
};

LowBalanceWarning.propTypes = {
    balance: PropTypes.number.isRequired,
};

export default LowBalanceWarning;
