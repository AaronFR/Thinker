// VerifyEmail.js
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

import Navigation from "../../components/Navigation";
import { verifyEndpoint } from '../../constants/endpoints';

import './styles/Verify.css'

const VerifyEmail = (isAuthenticated) => {
  const [verificationStatus, setVerificationStatus] = useState({
    success: null,
    message: '',
    promotionApplied: false,
    lastPromotion: false,
  });
  const query = new URLSearchParams(useLocation().search);
  const token = query.get('token');
  let promption_text = ''

  const success_message = 'Your email address has been successfully verified! You can now use and top up your balance. '
  const error_message = 'Your email address has been unsuccessfully, not verified! ..-successfully not verified.. unsuccessfully?  (something has gone wrong)'

  useEffect(() => {
    const verify = async () => {
      try {
        const response = await fetch(verifyEndpoint + `?token=${token}`, {
          method: 'GET',
        });

        if (response.ok) {
          const promotionData = await response.json();

          setVerificationStatus({
            success: true,
            message: success_message,
            promotionApplied: promotionData.promotion_applied || false,
            lastPromotion: promotionData.last_promotion || false,
          });

        } else {
          console.log("Incorrect response", response)

          setVerificationStatus({
            success: false,
            message: error_message,
          });
          throw new Error("Invalid Verification");
        }
      } catch (error) {
        setVerificationStatus({
          success: false,
          message: error?.response?.data?.error || error_message,
        });
      }
    };

    if (token) {
      verify();
    } else {
      setVerificationStatus({
        success: false,
        message: 'Invalid verification link.',
      });
    }
  }, [token]);

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
