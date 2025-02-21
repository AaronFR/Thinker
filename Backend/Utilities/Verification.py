import datetime
import logging
import os

import jwt

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from Constants.Constants import THE_THINKER_AI_DOMAIN_URL, SENDGRID_API_KEY


def send_verification_email(email: str):
    """
    Sends a verification email to the registered email address

    :param email: The entered email, (already passed check to confirm email isn't in database)
    """

    token = jwt.encode({
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, os.getenv("JWT_SECRET_KEY"), algorithm='HS256')

    verification_link = f"{THE_THINKER_AI_DOMAIN_URL}/verify?token={token}"

    message = Mail(
        from_email='no-reply@em6129.thethinkerai.com',
        to_emails=email,
        subject='Verify your email for The Thinker AI',
        html_content=f'''
            <p>Thank you for registering with The Thinker!</p>
            <p>Please verify your email by clicking the link below:</p>
            <a href="{verification_link}">Verify Email</a>
            <small>This link will expire in 24 hours.</small>
            
            <p>
                <br>
                If you did not create a new account feel free to ignore this message, the account can't be used till
                verified and you can assume control of it via password reset (in future 😅).
            </p>
        '''
    )
    try:
        sg = SendGridAPIClient(os.getenv(SENDGRID_API_KEY))
        response = sg.send(message)
        logging.info(f"Verification email sent to {email} with status code {response.status_code}")
    except Exception:
        logging.exception("Failure to send verification email!")
        raise "Failure to send verification email!"
