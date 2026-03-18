import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_port(port):
    import subprocess
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True, capture_output=True, text=True
        )
        for line in result.stdout.strip().split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                pid = line.strip().split()[-1]
                subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                print(f"Killed existing process {pid} on port {port}")
                return True
    except Exception as e:
        print(f"Could not auto-kill port: {e}")
    return False

def main():
    import uvicorn
    port = 8000

    if is_port_in_use(port):
        print(f"Port {port} is in use. Attempting to free it...")
        killed = kill_port(port)
        if not killed:
            print(f"Could not free port {port}.")
            print(f"Manually run: netstat -ano | findstr :{port}")
            print(f"Then: taskkill /PID <PID> /F")
            sys.exit(1)
        import time
        time.sleep(2)

    print("=" * 60)
    print("  COMPETITIVE INTELLIGENCE SYSTEM")
    print(f"  API Server starting on http://localhost:{port}")
    print(f"  Dashboard: http://localhost:{port}")
    print(f"  API docs:  http://localhost:{port}/docs")
    print("  Pipeline runs ONLY when triggered from the dashboard.")
    print("=" * 60)

    uvicorn.run("api_server:app", host="127.0.0.1", port=port, reload=False)

if __name__ == "__main__":
    main()
