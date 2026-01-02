"""Entry point for the Flask application.

This module creates the Flask app using the application factory.
Can be used both for development and production (WSGI).

Development:
    flask run

Production (PythonAnywhere):
    from flask_app import app as application
"""

import os
from app import create_app
from app.config import DevelopmentConfig, ProductionConfig

# Select config based on environment
config_class = (
    ProductionConfig if os.getenv("FLASK_ENV") == "production" else DevelopmentConfig
)

# Create app instance
app = create_app(config_class)

if __name__ == "__main__":
    app.run()
