# GitHub Gists API

A simple HTTP web server API that fetches and displays publicly available GitHub Gists for any user.

## Features

- Fetch GitHub user gists via REST API
- Response caching for improved performance
- Health check endpoint
- Comprehensive unit tests
- Docker containerization
- GitHub token support for higher API rate limits

## Prerequisites

- Python 3.11+ (for local development)
- Docker (for containerized deployment)
- Git

## Installation & Local Development

### 1. Clone or Navigate to Project

```bash
cd /Users/shrikantchilwant/Documents/equal-expert
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application Locally

```bash
python app.py
```

The API will start on `http://localhost:8080`

## Running Tests

```bash
# Run all tests
pytest test_app.py -v

# Run tests with coverage report
pytest test_app.py -v --cov=app

# Run specific test
pytest test_app.py::test_get_user_gists_success -v
```

## API Usage

### Get User Gists

**Endpoint:** `GET /<USERNAME>`

**Example:**
```bash
curl http://localhost:8080/octocat
```

**Response:**
```json
{
  "username": "octocat",
  "gist_count": 2,
  "gists": [
    {
      "id": "gist1",
      "url": "https://api.github.com/gists/gist1",
      "description": "Test Gist 1",
      "files": ["file1.txt"],
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Health Check

**Endpoint:** `GET /health`

```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t github-gists-api:latest .
```

### Run Container

```bash
docker run -p 8080:8080 github-gists-api:latest
```

### Run with GitHub Token (Optional)

For higher API rate limits, provide a GitHub personal access token:

```bash
docker run -p 8080:8080 \
  -e GITHUB_TOKEN=your_github_token_here \
  github-gists-api:latest
```

### Test Running Container

```bash
# Health check
curl http://localhost:8080/health

# Get gists for octocat
curl http://localhost:8080/octocat
```

### Stop Container

```bash
docker stop <container_id>
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub personal access token for higher rate limits | No |
| `PORT` | Port number (default: 8080) | No |
| `FLASK_APP` | Flask application module | No |

## Project Structure

```
equal-expert/
├── app.py              # Main Flask application
├── test_app.py         # Unit tests
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
└── README.md          # This file
```

## Troubleshooting

### Port 8080 Already in Use

```bash
# Find process using port 8080
lsof -i :8080

# Kill process (replace PID with actual process ID)
kill -9 <PID>
```

### Import Errors When Running Tests

Ensure you're in the virtual environment and dependencies are installed:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Docker Build Fails

Try rebuilding without cache:

```bash
docker build --no-cache -t github-gists-api:latest .
```

## API Rate Limits

- **Without GitHub Token:** 60 requests/hour per IP
- **With GitHub Token:** 5,000 requests/hour per user

To get a GitHub token:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token"
3. Select `public_repo` scope
4. Copy and use the token

## Testing Against Live GitHub API

Once running, test with real GitHub users:

```bash
# Test with octocat (GitHub's test user)
curl http://localhost:8080/octocat

# Test with another user
curl http://localhost:8080/torvalds
```

## Dependencies

- **Flask** - Web framework
- **requests** - HTTP library for GitHub API calls
- **pytest** - Testing framework
- **pytest-cov** - Code coverage reports
