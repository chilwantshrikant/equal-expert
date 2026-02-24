"""Tests for the GitHub Gists API."""

import pytest
import json
from unittest.mock import patch, MagicMock
from app import app, get_user_gists


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_gists_response():
    """Mock GitHub API response for gists."""
    return [
        {
            "id": "gist1",
            "html_url": "https://gist.github.com/octocat/gist1",
            "description": "Test gist 1",
            "created_at": "2023-01-01T00:00:00Z",
            "files": {
                "test.py": {"filename": "test.py"},
                "test.txt": {"filename": "test.txt"}
            }
        },
        {
            "id": "gist2",
            "html_url": "https://gist.github.com/octocat/gist2",
            "description": None,
            "created_at": "2023-01-02T00:00:00Z",
            "files": {
                "readme.md": {"filename": "readme.md"}
            }
        }
    ]


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_index_endpoint(self, client):
        """Test the root endpoint returns API documentation."""
        response = client.get("/")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "name" in data
        assert "GitHub Gists API" in data["name"]
    
    def test_get_gists_success(self, client, mock_gists_response):
        """Test successful retrieval of gists."""
        with patch("app.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_gists_response
            mock_get.return_value = mock_response
            
            response = client.get("/octocat")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["success"] is True
            assert data["username"] == "octocat"
            assert data["gist_count"] == 2
            assert len(data["gists"]) == 2
            
            # Check first gist
            assert data["gists"][0]["id"] == "gist1"
            assert data["gists"][0]["description"] == "Test gist 1"
            assert "test.py" in data["gists"][0]["files"]
            
            # Check second gist (no description should return "No description")
            assert data["gists"][1]["description"] == "No description"
    
    def test_get_gists_user_not_found(self, client):
        """Test 404 response when user not found."""
        with patch("app.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            response = client.get("/nonexistentuser")
            assert response.status_code == 404
            
            data = json.loads(response.data)
            assert data["success"] is False
            assert "not found" in data["error"].lower()
    
    def test_get_gists_api_error(self, client):
        """Test 503 response when GitHub API fails."""
        with patch("app.requests.get") as mock_get:
            mock_get.side_effect = Exception("GitHub API error")
            
            response = client.get("/octocat")
            assert response.status_code == 503
            
            data = json.loads(response.data)
            assert data["success"] is False
            assert "Failed to fetch gists" in data["error"]
    
    def test_get_gists_empty_list(self, client):
        """Test user with no gists."""
        with patch("app.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            response = client.get("/someuser")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["success"] is True
            assert data["gist_count"] == 0
            assert data["gists"] == []
    
    def test_invalid_endpoint(self, client):
        """Test that invalid endpoints return 404."""
        response = client.get("/invalid/path")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["success"] is False


class TestGetUserGists:
    """Test the get_user_gists function."""
    
    def test_get_user_gists_success(self, mock_gists_response):
        """Test successful gist retrieval."""
        with patch("app.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_gists_response
            mock_get.return_value = mock_response
            
            result = get_user_gists("octocat")
            
            assert len(result) == 2
            assert result[0]["id"] == "gist1"
            assert result[0]["description"] == "Test gist 1"
            assert result[1]["description"] == "No description"
    
    def test_get_user_gists_user_not_found(self):
        """Test ValueError when user not found."""
        with patch("app.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            with pytest.raises(ValueError, match="not found"):
                get_user_gists("nonexistentuser")
    
    def test_get_user_gists_timeout(self):
        """Test timeout handling."""
        with patch("app.requests.get") as mock_get:
            mock_get.side_effect = TimeoutError()
            
            with pytest.raises(Exception):
                get_user_gists("octocat")
    
    def test_get_user_gists_empty(self):
        """Test user with no gists."""
        with patch("app.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            result = get_user_gists("someuser")
            assert result == []


class TestIntegration:
    """Integration tests with real GitHub API (optional - may be skipped in CI)."""
    
    @pytest.mark.integration
    def test_octocat_real_api(self, client):
        """Test with real octocat user from GitHub API."""
        # This test uses the real GitHub API - no mocking
        response = client.get("/octocat")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["username"] == "octocat"
        # octocat should have some gists
        assert data["gist_count"] > 0
        assert len(data["gists"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
