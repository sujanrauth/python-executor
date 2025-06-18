import os
import json
import subprocess
import tempfile
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Main execution endpoint - accepts POST requests with Python code to execute
@app.route('/execute', methods=['POST'])
def execute_script():
    try:
        # Request validation to accept input in JSON format 
        # Having a non empty script field and main() function inside the script field value
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if not data or 'script' not in data:
            return jsonify({"error": "Missing 'script' field in request body"}), 400
        
        script = data['script']
        if not isinstance(script, str) or not script.strip():
            return jsonify({"error": "Script must be a non-empty string"}), 400
        
        if 'def main(' not in script:
            return jsonify({"error": "Script must contain a main() function"}), 400
        
        # Calling function that executes the python script safety
        result = execute_python_script(script)
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error executing script: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Function to execute the script safely while capturing the return and print(stdout) values
def execute_python_script(script):

    # Create a new temporary file called script.py
    # Having user requested script and code to capture results
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Add wrapper code to capture return value and stdout
        # Code is indented in this way to avoid indentation errors
        wrapper_script = f"""
import sys
import json
import io
from contextlib import redirect_stdout

# User script
{script}

# Execution wrapper
if __name__ == "__main__":
    stdout_capture = io.StringIO()
    
    try:
        with redirect_stdout(stdout_capture):
            result = main()
        
        # Validate that result is JSON serializable
        try:
            json.dumps(result)
        except (TypeError, ValueError):
            print(json.dumps({{"error": "main() function must return JSON-serializable data"}}))
            sys.exit(1)
        
        output = {{
            "result": result,
            "stdout": stdout_capture.getvalue()
        }}
        print(json.dumps(output))
        
    except Exception as e:
        error_output = {{
            "error": f"Script execution error: {{str(e)}}",
            "stdout": stdout_capture.getvalue()
        }}
        print(json.dumps(error_output))
        sys.exit(1)
"""
        f.write(wrapper_script)
        script_path = f.name
    
    try:
        # nsjail command to run the script.py with all the configuartions provided 
        # Run in standalone mode with memory limit of 512MB, CPU limit of 100 secs, file size limit of 1024 bytes
        # Mounted script.py, python interpreter, system libraries, user libraries and python packages as read only
        nsjail_cmd = [
            'nsjail',
            '--mode', 'o',
            '--time_limit', '30', 
            '--rlimit_as', '512', 
            '--rlimit_cpu', '100',      
            '--rlimit_fsize', '1024',    
            '--rlimit_nofile', '32', 
            '--bindmount', f'{script_path}:/app/script.py:ro', 
            '--bindmount', '/usr/bin/python3:/usr/bin/python3:ro',
            '--bindmount', '/lib:/lib:ro',
            '--bindmount', '/usr/lib:/usr/lib:ro',
            '--bindmount', '/usr/local/lib/python3.10/dist-packages:/usr/local/lib/python3.10/dist-packages:ro',
            '--cwd', '/',
            '--',
            '/usr/bin/python3', '/app/script.py'
        ]
        
        # Execute the script with security constraints
        # Capture both stdout and stderr, Return output as strings, not bytes
        # Kill process if it runs longer than 30 seconds
        result = subprocess.run(
            nsjail_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Check if the script execution failed (non-zero exit code)
        if result.returncode != 0:
            if result.stdout:
                try:
                    error_data = json.loads(result.stdout)
                    # Return structured error from the script.py
                    return error_data
                except json.JSONDecodeError:
                    pass
            # Return unstructured error from stderr if JSON parsing failed
            return {"error": f"Script execution failed: {result.stderr}"}
        
        # Script executed successfully, parse the JSON output
        try:
            output = json.loads(result.stdout)
            # Return the structured result from the script
            return output
        except json.JSONDecodeError:
            return {"error": "Failed to parse script output"}
            
    except subprocess.TimeoutExpired:
        return {"error": "Script execution timed out"}
    except Exception as e:
        return {"error": f"Execution error: {str(e)}"}
    finally:
        # Clean up: always try to delete the temporary script file
        try:
            # Remove the temporary script file
            os.unlink(script_path)
        except:
            pass
# Health check endpoint - used to monitor the system
@app.route('/health', methods=['GET'])
def health_check():
    # Return JSON with 200 OK status
    return jsonify({"status": "healthy"}), 200

# Start the Flask development server
if __name__ == '__main__':
    # Run server on all interfaces (0.0.0.0) on port 8080
    app.run(host='0.0.0.0', port=8080)
