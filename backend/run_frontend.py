import subprocess, os, sys

frontend = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
print(f"Frontend path: {frontend}")
print(f"Exists: {os.path.exists(frontend)}")

cmd = sys.argv[1] if len(sys.argv) > 1 else 'npm install'
r = subprocess.run(cmd, shell=True, cwd=frontend, text=True)
print("Exit code:", r.returncode)
