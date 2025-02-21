// VerifyEmail.js
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

import Navigation from "../../components/Navigation";
import { verifyEndpoint } from '../../constants/endpoints';

import './styles/Verify.css'

const VerifyEmail = (isAuthenticated) => {
  const [message, setMessage] = useState('');
  const query = new URLSearchParams(useLocation().search);
  const token = query.get('token');

  useEffect(() => {
    const verify = async () => {
      try {
        const response = await fetch(verifyEndpoint + `?token=${token}`, {
          method: 'GET',
        });

        if (response.ok == false) {
          throw Error("Invalid")
        }
        setMessage('Your email address has been succesffully verified! You can now use and top up your balance.');
      } catch (error) {
        setMessage(error?.response?.data?.error || 'Your email address has been unsuccesffully, not verified! ..-succesffully not verified.. unsuccesffully?\n(something has gone wrong)');
      }
    };

    if (token) {
      verify();
    } else {
      setMessage('Invalid verification link.');
    }
  }, [token]);

  return (
    <div className='container verify-background'>
      {isAuthenticated && <Navigation />}
      
      <div>
        <h2 className='centered'>Email Verification</h2>
        <p className='centered'>{message}</p>
      </div>
      
    </div>
  );
};

export default VerifyEmail;
