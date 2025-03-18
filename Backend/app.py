"""
Flask Backend Application
"""
import logging

import eventlet

from Utilities.LogsHandler import LogsHandler

eventlet.monkey_patch()

from App import create_app, socketio
app = create_app()


if __name__ == '__main__':
    LogsHandler.setup_logging()
    logging.info("Back end is running")

    # Correctly run the Flask application with SocketIO
    socketio.run(app, debug=True)
