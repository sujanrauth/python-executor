
import urllib.request
import urllib.error
import json
import sys

def test_api(base_url="http://localhost:8080"):
    print(f"Testing API: {base_url}")
    
    # Test for Basic requests
    tests = [
        ("Sample", "import os\nimport pandas as pd\nimport numpy as np\ndef main():\n    print(\"Hello\")\n    a = 2\n    b = a + 3\n    return {\"status\": b}"),
        ("Error", "Hello")
    ]
    
    for name, script in tests:
        print(f"\n{name}:")
        try:
            # Prepare the data
            data = {"script": script}
            json_data = json.dumps(data).encode('utf-8')
            
            # Create the request
            req = urllib.request.Request(
                f"{base_url}/execute",
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Make the request with timeout
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            if "error" in result:
                print(result['error'])
            else:
                print(result)
                    
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
        except Exception as e:
            print(e)
    
    # Test for Health check
    print(f"\nHealth check:")
    try:
        req = urllib.request.Request(f"{base_url}/health")
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"Status: {response.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    test_api(url)