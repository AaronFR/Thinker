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
  const error_message = 'Your email address has been unsuccesffully, not verified! ..-succesffully not verified.. unsuccesffully?<br>(something has gone wrong)'

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
        <p>
          {verificationStatus.success === null ? (
            "Verifying..."
          ) : verificationStatus.success ? (
            <>
              <p className='message'>{verificationStatus.message}</p>
              {verificationStatus.promotionApplied && !verificationStatus.lastPromotion && (
                <p className='promotion'>
                  <p>
                    Also you've been granted a promotional, <i>whole</i>, <b>singular</b>, <b className='big'><b className='big'><i>DOLLAR!</i></b></b>
                  </p>
                  <p>Try out the thinker, we hope it works for you.</p>
                </p>
              )}
              {verificationStatus.lastPromotion && (
                <p className='promotion'>Òooooo you got the <i>last</i> free trial dollar, <i className='big'>luuuucky!</i></p>
              )}
            </>
          ) : (
            verificationStatus.message
          )}
        </p>
      </div>
    </div>
  );
};

export default VerifyEmail;
