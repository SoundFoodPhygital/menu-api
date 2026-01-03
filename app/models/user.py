"""User model."""

from __future__ import annotations

import re
import typing as tp

from flask_login import UserMixin
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db

if tp.TYPE_CHECKING:
    from .menu import Menu


class User(db.Model, UserMixin):
    """User model for authentication and authorization."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_manager: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    menus: Mapped[list[Menu]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)

    @property
    def role(self) -> str:
        """Get user role as string."""
        if self.is_admin:
            return "admin"
        elif self.is_manager:
            return "manager"
        return "user"

    @classmethod
    def create(
        cls,
        username: str,
        password: str,
        is_admin: bool = False,
        is_manager: bool = False,
        email: str | None = None,
    ) -> User:
        """Factory method to create and persist a new user."""
        user = cls(
            username=username,
            email=email,
            is_admin=is_admin,
            is_manager=is_manager,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_by_username(cls, username: str) -> User | None:
        """Find user by username."""
        return db.session.execute(
            db.select(cls).where(cls.username == username)
        ).scalar()

    @classmethod
    def get_by_email(cls, email: str) -> User | None:
        """Find user by email."""
        return db.session.execute(db.select(cls).where(cls.email == email)).scalar()

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password strength.

        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        if not any(c.isalpha() for c in password):
            return False, "Password must contain at least one letter"
        return True, ""
