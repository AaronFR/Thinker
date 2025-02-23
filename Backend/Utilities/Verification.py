import datetime
import logging
import os

import jwt

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from Constants.Constants import THE_THINKER_AI_DOMAIN_URL, SENDGRID_API_KEY
from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB


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
        from_email='verification@em6129.thethinkerai.com',
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


def apply_new_user_promotion(email: str):
    """
    Attempt to add new account promotion
    ToDo: Investigate applying a lock to neo4j for these types of write operations
    """
    if NodeDB().check_new_user_promotion_active():
        remaining_new_user_promotions = NodeDB().add_new_user_promotion(email)
        if remaining_new_user_promotions is not None:
            promotional_text = promotion_applied_text(remaining_new_user_promotions)
    else:
        promotional_text = (
            "<p>Unfortunately we're out of new user promotions, this limit is to avoid malicious attacks, so "
            "contact us and we might be able to give you some free credit later."
            "</p>"
        )
        # ToDo: consider email alert to system email
        logging.warning(f"Could not apply new_user_promotion for [{email}] !")

    return promotional_text


def promotion_applied_text(remaining_new_user_promotions: int | None):
    """
    Additional text to inform the user they have received their free user trail promotion or not.
    This is not guaranteed but as long as it's viable new user will get a free dollar to figure out if The Thinker
    AI works for them
    # ToDo: consider email alert to system email in each case

    :param remaining_new_user_promotions: The remaining number of new user promotions left
    :return: html content related to the status of their new user promotion
    """
    promotional_text = (
        "<p>As a new user you start with a <i>whole</i>, <b>singular</b> <u><b><i>DOLLAR!</i></b></u></p>"
        "But yeah use it and see if The Thinker AI works for you."
    )
    if remaining_new_user_promotions == 0:
        promotional_text += (
            "<br>"
            "<p>ALSO yours was the last new user promotion available (currently), <i>luuuuuuucky.</i></p>"
        )
        logging.warning("New user promotions depleted!")
    elif remaining_new_user_promotions < 10:
        promotional_text += (
            "<br>"
            f"<p>(We are at <i>just</i>{remaining_new_user_promotions} free trail's left btw)</p>"
        )
        logging.warning("New user promotions nearly-depleted!")

    return promotional_text
