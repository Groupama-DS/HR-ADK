import vertexai
from vertexai.preview import reasoning_engines
import sys

# --- CONFIGURATION ---
PROJECT_ID = "prj-hackathon-team2"
LOCATION = "europe-west4"
REASONING_ENGINE_ID = "1451073873687609344"

try:
    print("--> Step 1: Script started.")
    sys.stdout.flush() # Forces the print to appear immediately

    print("--> Step 2: Initializing Vertex AI SDK...")
    sys.stdout.flush()
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    print("--> Step 3: Vertex AI SDK Initialized.")
    sys.stdout.flush()

    print(f"--> Step 4: Connecting to Reasoning Engine handle: {REASONING_ENGINE_ID}...")
    sys.stdout.flush()
    # This step is local and should be instant
    reasoning_engine = reasoning_engines.ReasoningEngine(REASONING_ENGINE_ID)
    print("--> Step 5: Reasoning Engine handle created.")
    sys.stdout.flush()

    print("--> Step 6: Sending query... (This is the most likely place for a hang)")
    sys.stdout.flush()
    response = reasoning_engine.query(
        input="What are my benefits?"
    )
    # If the script gets here, it has succeeded
    print("--> Step 7: Received response from agent.")
    sys.stdout.flush()


    print("\n" + "="*50)
    print("--- SUCCESS! ---")
    print("="*50 + "\n")
    print("Received response:")
    print(response)

except Exception as e:
    print("\n" + "="*50)
    print("--- FAILED ---")
    print("="*50 + "\n")
    print(f"An error occurred: {e}")