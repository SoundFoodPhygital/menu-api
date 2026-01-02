"""Admin authentication routes blueprint."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from ..extensions import limiter
from ..models import User
from .views import AdminLoginForm

admin_auth_bp = Blueprint("admin_auth", __name__, url_prefix="/admin")


@admin_auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    """Admin login page."""
    if current_user.is_authenticated:
        if current_user.is_admin or current_user.is_manager:
            return redirect(url_for("admin.index"))
        flash("Access denied. Admin or Manager role required.", "error")

    form = AdminLoginForm()

    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)

        if user and user.check_password(form.password.data):
            if user.is_admin or user.is_manager:
                login_user(user)
                flash("Login successful!", "success")
                next_page = request.args.get("next")
                return redirect(next_page or url_for("admin.index"))
            else:
                flash("Access denied. Admin or Manager role required.", "error")
        else:
            flash("Invalid username or password.", "error")

    return render_template("admin_login.html", form=form)


@admin_auth_bp.route("/logout")
def logout():
    """Admin logout."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin_auth.login"))
