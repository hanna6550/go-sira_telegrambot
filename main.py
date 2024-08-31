import subprocess

# Start the first script
p1 = subprocess.Popen(["python", "app.py"])

# Start the second script
p2 = subprocess.Popen(["python", "employeer.py"])

# Wait for both scripts to finish
p1.wait()
p2.wait()
