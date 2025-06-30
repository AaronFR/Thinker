import datetime
import logging
import os

import jwt
from deprecated.classic import deprecated

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from Constants.Constants import SENDGRID_API_KEY
from Data.Neo4j.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB


@deprecated
def send_verification_email(email: str):
    """
    #ToDo: Password reset method
    Sends a verification email to the registered email address

    :param email: The entered email, (already passed check to confirm email isn't in database)
    """
    expiration_date = datetime.datetime.utcnow() + datetime.timedelta(hours=24)

    token = jwt.encode({
        'email': email,
        'exp': expiration_date
    }, os.getenv("JWT_SECRET_KEY"), algorithm='HS256')

    verification_link = f"https://thethinkerai.com/verify?token={token}"

    message = Mail(
        from_email='verification@em6129.thethinkerai.com',
        to_emails=email,
        subject='Verify your email for The Thinker AI - Get free credit',
        html_content=f'''
            <p>Thank you for registering with The Thinker AI!</p>
            <p>Please verify you own this email by clicking below</p>
            <a href="{verification_link}">Verify Email</a>
            <small>This link will expire in 24 hours.</small>
            
            <br>
            <p>When verified, we will give you a free dollar of credit to get started.</p>
            
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
        logging.info(f"Verification email sent to {email} with status code {response.status_code} and expiration date {expiration_date}")
    except Exception:
        logging.exception("Failure to send verification email!")
        raise Exception("Failure to send verification email!")


def apply_new_user_promotion(email: str):
    """
    Attempt to add new account promotion
    ToDo: Investigate applying a lock to neo4j for these types of write operations

    email: The email of the user who will receive the 1 dollar promotion to
    return: a tuple containing two booleans: was the promotion applied, and was it the *last* promotion
    """
    promotion_applied = False
    last_promotion = False

    if NodeDB().check_new_user_promotion_active():
        remaining_new_user_promotions = NodeDB().add_new_user_promotion(email)

        if remaining_new_user_promotions is not None:
            promotion_applied = True
            logging.info(f"Promotion applied for {email}")
            if remaining_new_user_promotions == 0:
                last_promotion = True
        else:
            logging.info("1$ Promotion could not be applied")
    else:
        logging.error("New user not found in database!")

    return promotion_applied, last_promotion
