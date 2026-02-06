import subprocess
import time
import os
import signal
import sys

def main():
    root_dir = os.getcwd()

    # Ensure src is in python path
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(root_dir, "src")

    # Start Backend
    print("Starting Backend on http://localhost:8000 ...")
    backend = subprocess.Popen(
        ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=root_dir,
        env=env
    )

    # Start Frontend
    print("Starting Frontend on http://localhost:3000 ...")
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=os.path.join(root_dir, "web"),
        env=env
    )

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        sys.exit(0)

if __name__ == "__main__":
    main()
