"""GitHub Gists API - A simple HTTP web server for retrieving user gists."""

import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)

# GitHub API base URL
GITHUB_API_BASE = "https://api.github.com"

# Optional: GitHub token from environment for higher rate limits
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Headers for GitHub API requests
HEADERS = {}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"
HEADERS["Accept"] = "application/vnd.github.v3+json"


def get_user_gists(username):
    """
    Fetch all public gists for a given GitHub user.
    
    Args:
        username (str): GitHub username
        
    Returns:
        list: List of gist objects with id, url, description, and created_at
        
    Raises:
        requests.exceptions.RequestException: If API request fails
        ValueError: If user not found
    """
    url = f"{GITHUB_API_BASE}/users/{username}/gists"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 404:
            raise ValueError(f"User '{username}' not found")
        
        response.raise_for_status()
        
        gists = response.json()
        
        # Extract relevant fields from each gist
        result = []
        for gist in gists:
            result.append({
                "id": gist.get("id"),
                "url": gist.get("html_url"),
                "description": gist.get("description") or "No description",
                "created_at": gist.get("created_at"),
                "files": list(gist.get("files", {}).keys())
            })
        
        return result
        
    except requests.exceptions.Timeout:
        raise requests.exceptions.RequestException("Request to GitHub API timed out")
    except requests.exceptions.RequestException as e:
        raise e


@app.route("/<username>", methods=["GET"])
def get_gists(username):
    """
    Get public gists for a GitHub user.
    
    Args:
        username (str): GitHub username
        
    Returns:
        JSON response with list of gists or error message
    """
    try:
        gists = get_user_gists(username)
        return jsonify({
            "success": True,
            "username": username,
            "gist_count": len(gists),
            "gists": gists
        }), 200
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to fetch gists: {str(e)}"
        }), 503


@app.route("/", methods=["GET"])
def index():
    """Root endpoint with API documentation."""
    return jsonify({
        "success": True,
        "name": "GitHub Gists API",
        "description": "Retrieve public gists for any GitHub user",
        "usage": "GET /<username>",
        "example": "GET /octocat",
        "response": {
            "success": True,
            "username": "string",
            "gist_count": "integer",
            "gists": [
                {
                    "id": "string",
                    "url": "string",
                    "description": "string",
                    "created_at": "string",
                    "files": ["string"]
                }
            ]
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "success": False,
        "error": "Endpoint not found. Use /<username> to get gists."
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == "__main__":
    # Run the Flask app
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
