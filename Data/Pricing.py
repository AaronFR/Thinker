from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB
from Utilities import Globals


class Pricing:

    @staticmethod
    def get_user_balance():
        return NodeDB().get_user_balance()

    @staticmethod
    def top_up_user_balance(sum):
        try:
            NodeDB().update_user_balance(sum)
            return {
                "status_code": 200,
                "message": f"User balance successfully topped up by ${sum}."
            }
        except Exception as e:
            return {
                "status_code": 500,
                "message": f"Failed to update user balance: {str(e)}"
            }

    """
    ToDo: This isn't actually a users session cost, this is the money spent on the server since deployment
    """
    @staticmethod
    def get_session_cost():
        return Globals.current_request_cost
