"""Database initialization module.

This module handles automatic database creation, table setup,
and seeding of default data when the application starts.
"""

import logging
import os

from flask import Flask
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError

from .extensions import db

logger = logging.getLogger(__name__)


def init_database(app: Flask) -> bool:
    """Initialize database if needed.

    This function checks if the database exists and has the required tables.
    If not, it creates them and seeds default data.

    Args:
        app: Flask application instance

    Returns:
        bool: True if initialization was performed, False if DB was already set up
    """
    with app.app_context():
        try:
            # Try to connect and check if tables exist
            if _database_needs_init():
                logger.info("Database needs initialization...")
                _create_tables()
                _seed_default_data(app)
                _create_admin_user(app)
                logger.info("Database initialization completed successfully!")
                return True
            else:
                logger.info("Database already initialized.")
                return False
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise


def _database_needs_init() -> bool:
    """Check if database needs initialization.

    Returns:
        bool: True if database needs to be initialized
    """
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        # Check for essential tables
        required_tables = ["user", "emotion", "texture", "shape"]
        existing_required = [t for t in required_tables if t in tables]

        if not existing_required:
            logger.info("No tables found, database needs initialization")
            return True

        # Check if user table has any data
        from .models import User

        user_count = User.query.count()
        if user_count == 0:
            logger.info("User table is empty, will create admin user")
            return True

        return False

    except (OperationalError, ProgrammingError) as e:
        # Database doesn't exist or can't connect
        logger.info(f"Database connection issue: {e}")
        return True


def _create_tables():
    """Create all database tables."""
    logger.info("Creating database tables...")
    db.create_all()
    logger.info("Tables created successfully")


def _seed_default_data(app: Flask):
    """Seed default attributes (emotions, textures, shapes)."""
    from .models import Emotion, Shape, Texture

    logger.info("Seeding default attributes...")

    emotions = [
        "joy",
        "anger",
        "fear",
        "sadness",
        "surprise",
        "satisfaction",
        "gratitude",
        "hope",
        "love",
        "serenity",
        "euphoria",
        "conviviality",
        "playfulness",
    ]

    textures = [
        "rough",
        "soft",
        "hard",
        "creamy",
        "crunchy",
        "liquid",
        "viscous",
        "solid",
        "hollow",
        "dense",
        "porous",
        "airy",
    ]

    shapes = [
        "sharp",
        "round",
        "smooth",
        "symmetric",
        "asymmetric",
        "compact",
        "loose",
    ]

    for description in emotions:
        if not Emotion.query.filter_by(description=description).first():
            db.session.add(Emotion(description=description))

    for description in textures:
        if not Texture.query.filter_by(description=description).first():
            db.session.add(Texture(description=description))

    for description in shapes:
        if not Shape.query.filter_by(description=description).first():
            db.session.add(Shape(description=description))

    db.session.commit()
    logger.info("Default attributes seeded successfully")


def _create_admin_user(app: Flask):
    """Create default admin user from environment variables."""
    from .models import User

    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD", "admin123")
    email = os.environ.get("ADMIN_EMAIL", "admin@example.com")

    # Check if admin already exists (by username or email)
    if User.get_by_username(username):
        logger.info(f"Admin user '{username}' already exists")
        return

    if email and User.query.filter_by(email=email).first():
        logger.info(f"User with email '{email}' already exists")
        return

    logger.info(f"Creating admin user '{username}'...")

    try:
        user = User.create(
            username=username,
            password=password,
            email=email,
            is_admin=True,
            is_manager=True,
        )
        logger.info(f"Admin user '{username}' created successfully (ID: {user.id})")
    except IntegrityError:
        # Another worker might have created the user already
        db.session.rollback()
        logger.info(f"Admin user '{username}' was created by another process")


def check_database_connection(app: Flask) -> bool:
    """Check if database connection is working.

    Args:
        app: Flask application instance

    Returns:
        bool: True if connection is successful
    """
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
