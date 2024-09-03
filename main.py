import subprocess

# Start the first script
applicant = subprocess.Popen(["python", "applicant.py"])

# Start the second script
employer = subprocess.Popen(["python", "employeer.py"])

# Wait for both scripts to finish
applicant.wait()
employer.wait()
