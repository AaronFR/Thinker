from Data.NodeDatabaseManagement import NodeDatabaseManagement as NodeDB
from Utilities import Globals


class Pricing:

    @staticmethod
    def get_user_balance():
        return NodeDB().get_user_balance()

    """
    ToDo: This isn't actually a users session cost, this is the money spent on the server since deployment
    """
    @staticmethod
    def get_session_cost():
        return Globals.current_request_cost
