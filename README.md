# Python Code Execution Service

A secure API service that executes arbitrary Python code in a sandboxed environment using nsjail.

## Features

- Secure execution of Python scripts using nsjail sandboxing
- Input validation and error handling
- Support for common libraries (os, pandas, numpy)
- Lightweight Docker image
- Timeout protection (30 seconds)
- Memory and resource limits

## Quick Start

### Running Locally

```bash
# Build the Docker image
docker build -t python-executor .

# Run the service
docker run --privileged -p 8080:8080 python-executor
```

The service will be available at `http://localhost:8080`

### Testing the API

#### Example cURL request (local):

```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "import os\nimport pandas as pd\nimport numpy as np\ndef main():\n    print(\"Hello\")\n    a = 2\n    b = a + 3\n    return {\"status\": b}"}'
```

#### Example cURL request (Cloud Run):

```bash
curl -X POST https://your-service-url.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "import os\nimport pandas as pd\nimport numpy as np\ndef main():\n    print(\"Hello\")\n    a = 2\n    b = a + 3\n    return {\"status\": b}"}'
```

#### Expected Response:

```json
{   
    "result":{
        "status": 5
    },
    "stdout": "Hello\n"
}
```

## API Specification

### POST /execute

Executes a Python script and returns the result of the `main()` function.

**Request Body:**
```json
{
  "script": "def main():\n    return {'hello': 'world'}"
}
```

**Response:**
```json
{
  "result": {...},  // Return value of main() function
  "stdout": "..."   // Captured stdout from script execution
}
```

**Error Response:**
```json
{
  "error": "Error description"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Requirements

- The script must contain a `main()` function
- The `main()` function must return JSON-serializable data
- Scripts are executed with a 30-second timeout
- Memory is limited to 512MB
- Network access is disabled for security

## Available Libraries

The following Python libraries are available in the execution environment:
- Standard library modules (os, json, sys, etc.)
- pandas
- numpy

## Security Features

- **nsjail sandboxing**: Scripts run in isolated containers
- **Resource limits**: CPU, memory, and file size limits
- **Timeout protection**: Scripts are terminated after 30 seconds
- **Network isolation**: No external network access
- **File system restrictions**: Limited file system access

## Deployment to Google Cloud Run

1. Build and push to Container Registry:
```bash
# Tag the image
docker tag python-executor gcr.io/YOUR_PROJECT_ID/python-executor

# Push to registry
docker push gcr.io/YOUR_PROJECT_ID/python-executor
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy python-executor \
  --image gcr.io/YOUR_PROJECT_ID/python-executor \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 60s
```

## Error Handling

The service handles various error conditions:

- Missing or invalid JSON in request
- Missing `script` field
- Scripts without `main()` function
- Non-JSON-serializable return values
- Script execution errors
- Timeout errors
- Resource limit exceeded

## Development

### Project Structure
```
.
├── app.py              # Flask application
├── nsjail.cfg          # nsjail configuration
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container configuration
└── README.md          # This file
```

### Testing Different Scripts

#### Simple calculation:
```json
{
  "script": "def main():\n    return {'result': 2 + 2}"
}
```

#### Using pandas:
```json
{
  "script": "import pandas as pd\n\ndef main():\n    df = pd.DataFrame({'a': [1, 2, 3]})\n    return {'mean': df['a'].mean()}"
}
```

#### With stdout output:
```json
{
  "script": "def main():\n    print('Hello, World!')\n    return {'message': 'success'}"
}
```

## Limitations

- 30-second execution timeout
- 512MB memory limit
- No network access
- Limited file system access
- Only JSON-serializable return types supported