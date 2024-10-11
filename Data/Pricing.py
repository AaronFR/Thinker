from Utilities import Globals


class Pricing():

    @staticmethod
    def get_session_cost():
        return Globals.current_request_cost
