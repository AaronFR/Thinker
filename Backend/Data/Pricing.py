import logging

from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB
from Utilities import Globals


class Pricing:
    """
    Pricing management class for handling user balances and session costs.
    """

    @staticmethod
    def get_user_balance() -> float:
        """Retrieves the current user balance.

        :return: The current user balance.
        """
        return NodeDB().get_user_balance()

    @staticmethod
    def top_up_user_balance(amount: float) -> dict:
        """Tops up the user's balance.

        :param amount: The amount to add to the user's balance (must be positive).
        :return: A dictionary containing the status of the operation.
        :raises ValueError: If the amount is not positive.
        """
        if amount <= 0:
            raise ValueError("Amount to top up must be greater than zero.")

        try:
            NodeDB().update_user_balance(amount)
            return {
                "status_code": 200,
                "message": f"User balance successfully topped up by ${amount}."
            }
        except Exception as e:
            logging.exception(f"FAILED TO UPDATE USER BALANCE!: {str(e)}")
            return {
                "status_code": 500,
                "message": f"Failed to update user balance: {str(e)}"
            }

    @staticmethod
    def get_session_cost() -> float:
        """Fetches the current session cost accumulated since deployment.
        ToDo: This isn't actually a users session cost, this is the money spent on the server since deployment

        :return: The current session cost.
        """
        return Globals.current_request_cost

