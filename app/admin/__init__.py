"""Admin package - exports admin setup functions."""

from .routes import admin_auth_bp
from .views import init_admin

__all__ = ["admin_auth_bp", "init_admin"]
