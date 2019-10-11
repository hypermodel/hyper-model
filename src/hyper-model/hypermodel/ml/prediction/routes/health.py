
import logging

from flask import Flask


def bind_health_routes(app: Flask):
    """
    Binds new routes to the Flask App providing functionality about
    the health of the application.

    Args:
        app (Flask): The app to bind the new routes

    Returns:
        Nothing
    """

    @app.route('/healthz')
    def health():
        logging.info("api: /healthz")
        return "I am healthy!"

    @app.route('/testing')
    def testing():
        logging.info("api: /testing")
        return "Hi tez, how are you?"
