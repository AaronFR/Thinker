// VerifyEmail.js
import React from 'react';

import Navigation from "../../components/Navigation";

import './styles/Verify.css'

const VerifyEmail = (isAuthenticated) => {
  return (
    <div className='container verify-background'>
      {isAuthenticated && <Navigation />}

      <div>
        <h2 className='centered'>Email Verification</h2>
        <h3>
          NO LONGER IN USE
        </h3>
        <p>As it turns out people don't want to click on hyperlinks from a company they haven't heard of before. <i>huh</i></p>
      </div>
    </div>
  );
};

export default VerifyEmail;
