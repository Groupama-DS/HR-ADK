import sys
import datetime

print(f"--> {datetime.datetime.now()}: Script started. About to import vertexai...")
sys.stdout.flush()

# This is the line we are testing. The entire program hangs here.
import vertexai

# If you see this line, it means the import succeeded, which would be a huge surprise.
print(f"--> {datetime.datetime.now()}: SUCCESS: 'import vertexai' completed.")
sys.stdout.flush()