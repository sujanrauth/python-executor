# Python Code Execution Service

A secure API service that executes arbitrary Python code in a sandboxed environment using nsjail.

## Features

- Secure execution of Python scripts using nsjail sandboxing
- Input validation and error handling
- Support for common libraries (os, pandas, numpy)
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
curl -X POST http://3.148.187.65:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "import os\nimport pandas as pd\nimport numpy as np\ndef main():\n    print(\"hello\")\n    a = 2\n    b = a + 3\n    return {\"status\": b}"}'
```

**Note:** Google Cloud Run does not support the ``--privileged`` flag required by ``nsjail``, which prevents the ``/execute`` ``POST`` endpoint from working correctly in that environment. This is because nsjail relies on privileged features such as mount and dependency binding to keep the Docker image lightweight and to dynamically execute user-submitted scripts.
- ✅ The health check endpoint ``/health`` works correctly on Cloud Run.
- ❌ The ``/execute`` endpoint does not due to the lack of privileged container support.

```bash
curl https://api-service-fz4rdzczxq-uc.a.run.app/health     
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

## Testing Different Scripts

Run this command after the server is active

```bash
python3 test_api.py
```

## Demo
[![Demo](https://img.youtube.com/vi/1jhwrumuiPE/0.jpg)](https://youtu.be/1jhwrumuiPE)

## Benchmark 

The total time taken was approximately ``4 to 4.5 hours``, with the majority of the effort spent on understanding and correctly implementing ``nsjail`` for secure code execution.

