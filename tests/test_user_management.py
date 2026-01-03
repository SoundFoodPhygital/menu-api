"""Tests for user management endpoints (email update, password update, account deletion)."""


class TestUpdateEmail:
    """Tests for updating user email."""

    def test_update_email_success(self, client, auth_headers, test_user):
        """Test successful email update."""
        response = client.patch(
            "/auth/me/email",
            headers=auth_headers,
            json={"email": "newemail@example.com"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Email updated successfully"

    def test_update_email_invalid_format(self, client, auth_headers):
        """Test email update with invalid format."""
        response = client.patch(
            "/auth/me/email",
            headers=auth_headers,
            json={"email": "not-an-email"},
        )

        assert response.status_code == 400
        assert "Invalid email format" in response.get_json()["error"]

    def test_update_email_already_exists(self, client, auth_headers, app):
        """Test email update with email that already exists."""
        from app.models import User

        # Create another user with an email
        with app.app_context():
            User.create(
                username="otheruser",
                password="password123",
                email="existing@example.com",
            )

        response = client.patch(
            "/auth/me/email",
            headers=auth_headers,
            json={"email": "existing@example.com"},
        )

        assert response.status_code == 409
        assert "Email already in use" in response.get_json()["error"]

    def test_update_email_missing_data(self, client, auth_headers):
        """Test email update with missing email."""
        response = client.patch(
            "/auth/me/email",
            headers=auth_headers,
            json={},
        )

        assert response.status_code == 400
        assert "Email is required" in response.get_json()["error"]

    def test_update_email_no_data(self, client, auth_headers):
        """Test email update with no data."""
        response = client.patch("/auth/me/email", headers=auth_headers, json=None)

        # Flask returns 415 Unsupported Media Type when no JSON is provided
        assert response.status_code == 415

    def test_update_email_without_token(self, client):
        """Test email update without authentication."""
        response = client.patch(
            "/auth/me/email",
            json={"email": "newemail@example.com"},
        )

        assert response.status_code == 401

    def test_update_email_same_as_current(self, client, auth_headers, app, test_user):
        """Test updating email to the same value as current user's email."""
        from app.extensions import db
        from app.models import User

        # First, set an email for the test user
        with app.app_context():
            user = db.session.get(User, test_user)
            user.email = "current@example.com"
            db.session.commit()

        response = client.patch(
            "/auth/me/email",
            headers=auth_headers,
            json={"email": "current@example.com"},
        )

        assert response.status_code == 200


class TestUpdatePassword:
    """Tests for updating user password."""

    def test_update_password_success(self, client, auth_headers, test_user):
        """Test successful password update."""
        response = client.patch(
            "/auth/me/password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "newpassword456",
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Password updated successfully"

        # Verify new password works by logging in
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "newpassword456"},
        )
        assert login_response.status_code == 200

    def test_update_password_wrong_current(self, client, auth_headers):
        """Test password update with wrong current password."""
        response = client.patch(
            "/auth/me/password",
            headers=auth_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456",
            },
        )

        assert response.status_code == 401
        assert "Current password is incorrect" in response.get_json()["error"]

    def test_update_password_weak_password(self, client, auth_headers):
        """Test password update with weak password."""
        response = client.patch(
            "/auth/me/password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "weak",
            },
        )

        assert response.status_code == 400
        assert "at least 8 characters" in response.get_json()["error"]

    def test_update_password_no_digits(self, client, auth_headers):
        """Test password update with password missing digits."""
        response = client.patch(
            "/auth/me/password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "nodigitshere",
            },
        )

        assert response.status_code == 400
        assert "at least one digit" in response.get_json()["error"]

    def test_update_password_no_letters(self, client, auth_headers):
        """Test password update with password missing letters."""
        response = client.patch(
            "/auth/me/password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "12345678",
            },
        )

        assert response.status_code == 400
        assert "at least one letter" in response.get_json()["error"]

    def test_update_password_missing_fields(self, client, auth_headers):
        """Test password update with missing fields."""
        response = client.patch(
            "/auth/me/password",
            headers=auth_headers,
            json={"current_password": "testpassword123"},
        )

        assert response.status_code == 400
        assert (
            "Current password and new password are required"
            in response.get_json()["error"]
        )

    def test_update_password_no_data(self, client, auth_headers):
        """Test password update with no data."""
        response = client.patch("/auth/me/password", headers=auth_headers, json=None)

        # Flask returns 415 Unsupported Media Type when no JSON is provided
        assert response.status_code == 415

    def test_update_password_without_token(self, client):
        """Test password update without authentication."""
        response = client.patch(
            "/auth/me/password",
            json={
                "current_password": "testpassword123",
                "new_password": "newpassword456",
            },
        )

        assert response.status_code == 401


class TestDeleteAccount:
    """Tests for deleting user account."""

    def test_delete_account_success(self, client, auth_headers, test_user, app):
        """Test successful account deletion."""
        from app.extensions import db
        from app.models import User

        response = client.delete(
            "/auth/me",
            headers=auth_headers,
            json={"password": "testpassword123"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Account deleted successfully"

        # Verify user is deleted
        with app.app_context():
            user = db.session.get(User, test_user)
            assert user is None

    def test_delete_account_with_menus_and_dishes(
        self, client, auth_headers, test_user, test_menu, test_dish, app
    ):
        """Test account deletion cascades to menus and dishes."""
        from app.extensions import db
        from app.models import Dish, Menu, User

        response = client.delete(
            "/auth/me",
            headers=auth_headers,
            json={"password": "testpassword123"},
        )

        assert response.status_code == 200

        # Verify user, menu, and dish are all deleted
        with app.app_context():
            user = db.session.get(User, test_user)
            menu = db.session.get(Menu, test_menu)
            dish = db.session.get(Dish, test_dish)

            assert user is None
            assert menu is None
            assert dish is None

    def test_delete_account_wrong_password(self, client, auth_headers):
        """Test account deletion with wrong password."""
        response = client.delete(
            "/auth/me",
            headers=auth_headers,
            json={"password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "Password is incorrect" in response.get_json()["error"]

    def test_delete_account_missing_password(self, client, auth_headers):
        """Test account deletion with missing password."""
        response = client.delete(
            "/auth/me",
            headers=auth_headers,
            json={},
        )

        assert response.status_code == 400
        assert "Password confirmation is required" in response.get_json()["error"]

    def test_delete_account_no_data(self, client, auth_headers):
        """Test account deletion with no data."""
        response = client.delete("/auth/me", headers=auth_headers, json=None)

        # Flask returns 415 Unsupported Media Type when no JSON is provided
        assert response.status_code == 415

    def test_delete_account_without_token(self, client):
        """Test account deletion without authentication."""
        response = client.delete(
            "/auth/me",
            json={"password": "testpassword123"},
        )

        assert response.status_code == 401

    def test_delete_account_token_revoked(self, client, auth_headers, test_user):
        """Test that token is revoked after account deletion."""
        # Delete account
        client.delete(
            "/auth/me",
            headers=auth_headers,
            json={"password": "testpassword123"},
        )

        # Try to use token again
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 401
