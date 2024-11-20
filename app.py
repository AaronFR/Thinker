"""
Flask Backend Application
"""
import logging

import eventlet
eventlet.monkey_patch()

from App import create_app, socketio
app = create_app()


if __name__ == '__main__':
    logging.info("Back end is running")
    # Correctly run the Flask application with SocketIO
    socketio.run(app, debug=True)
