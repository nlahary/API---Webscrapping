import unittest
from unittest.mock import patch, MagicMock
from src.schemas.firebase import FirebaseUser
from src.services.firebase import get_users, verify_firebase_token, set_role, get_role
from firebase_admin import auth
from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient


class TestFirebaseUtils:

    @patch("src.services.firebase.auth.list_users")
    def test_get_users(self, mock_list_users: MagicMock):
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.uid = "user_id_123"
        mock_user.custom_claims = {"role": "admin"}
        mock_list_users.return_value.iterate_all.return_value = [mock_user]

        users = get_users()

        assert len(users) == 1
        assert users[0].email == "test@example.com"
        assert users[0].user_id == "user_id_123"
        assert users[0].role == "admin"

    @patch("src.services.firebase.auth.verify_id_token")
    def test_verify_firebase_token_valid(self, mock_verify_id_token: MagicMock):
        mock_verify_id_token.return_value = {
            "email": "test@example.com",
            "user_id": "user_id_123",
            "role": "admin"
        }

        user = verify_firebase_token("valid_token")

        assert user.email == "test@example.com"
        assert user.user_id == "user_id_123"
        assert user.role == "admin"

    @patch("src.services.firebase.auth.verify_id_token")
    def test_verify_firebase_token_invalid(self, mock_verify_id_token: MagicMock):
        mock_verify_id_token.side_effect = auth.InvalidIdTokenError(
            "Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            verify_firebase_token("invalid_token")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid Firebase token"

    @patch("src.services.firebase.auth.set_custom_user_claims")
    def test_set_role_valid(self, mock_set_custom_user_claims: MagicMock):
        set_role("user_id_123", "admin")
        mock_set_custom_user_claims.assert_called_once_with(
            "user_id_123", {"role": "admin"})

    def test_set_role_invalid(self):
        with pytest.raises(HTTPException) as exc_info:
            set_role("user_id_123", "invalid_role")

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid role"

    @patch("src.services.firebase.auth.get_user")
    def test_get_role_valid(self, mock_get_user: MagicMock):
        mock_user = MagicMock()
        mock_user.custom_claims = {"role": "admin"}
        mock_get_user.return_value = mock_user

        role = get_role("user_id_123")

        assert role == "admin"

    @patch("src.services.firebase.auth.get_user")
    def test_get_role_invalid(self, mock_get_user: MagicMock):
        mock_get_user.side_effect = Exception("Failed to get user")

        with pytest.raises(HTTPException) as exc_info:
            get_role("user_id_123")

        assert exc_info.value.status_code == 400
        assert "Failed to get role" in exc_info.value.detail


class TestFirebaseRoutes:

    @pytest.fixture
    def client(self):
        from main import get_application
        app = get_application()
        return TestClient(app, base_url="http://testserver")

    @patch("src.api.routes.authentication.verify_firebase_token")
    def test_protected_route_valid_token(self, mock_verify_firebase_token: MagicMock, client: TestClient):
        mock_verify_firebase_token.return_value = FirebaseUser(
            email="test@example.com", user_id="user_id_123", role="admin"
        )
        print(f"Mock called: {mock_verify_firebase_token.called}")

        response = client.get(
            "/active", headers={"Authorization": "Bearer valid_token"})
        print(f"Mock call count: {mock_verify_firebase_token.call_count}")

        print(response.json())
        assert mock_verify_firebase_token.called, "verify_firebase_token was not called"
        assert response.status_code == 200
        assert response.json() == {
            "email": "test@example.com",
            "user_id": "user_id_123",
            "role": "admin"
        }

    @patch("src.api.routes.authentication.verify_firebase_token")
    def test_protected_route_invalid_token(self, mock_verify_firebase_token: MagicMock, client: TestClient):
        mock_verify_firebase_token.side_effect = HTTPException(
            status_code=401, detail="Invalid Firebase token"
        )

        response = client.get(
            "/active", headers={"Authorization": "Bearer invalid_token"})

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid Firebase token"}

    @patch("requests.post")
    @patch("src.api.routes.authentication.set_role")
    def test_register_user(self, mock_set_role: MagicMock, mock_post: MagicMock, client: TestClient):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "localId": "user_id_123",
            "email": "test@example.com"
        }

        response = client.post("/register", json={
            "email": "test@example.com",
            "password": "password123",
            "role": "admin"
        })

        assert mock_set_role.called, "set_role was not called"
        assert response.status_code == 201
        assert response.json() == {
            "message": "Registration successful",
            "user_id": "user_id_123",
            "email": "test@example.com",
            "role": "admin"
        }

    @patch("requests.post")
    def test_login_user_valid(self, mock_post: MagicMock, client: TestClient):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "idToken": "test_token"
        }

        response = client.post("/token", data={
            "username": "test@example.com",
            "password": "password123"
        })

        assert response.status_code == 200
        assert response.json() == {
            "access_token": "test_token",
            "token_type": "bearer"
        }

    @patch("requests.post")
    def test_login_user_invalid(self, mock_post: MagicMock, client: TestClient):
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "error": {"message": "INVALID_PASSWORD"}
        }

        response = client.post("/token", data={
            "username": "test@example.com",
            "password": "wrongpassword"
        })

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Login failed: INVALID_PASSWORD"
        }


if __name__ == "__main__":
    unittest.main()
