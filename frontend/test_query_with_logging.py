import logging
import sys
import vertexai
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv
load_dotenv()


# --- STEP 1: ENABLE VERBOSE DEBUG LOGGING ---
# This will print every single action the Google Cloud libraries are taking.
# The output will be very long, but it will show us where it hangs.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logging.getLogger("google.auth").setLevel(logging.DEBUG)
logging.getLogger("google.api_core").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("requests").setLevel(logging.DEBUG)


# --- STEP 2: YOUR REGULAR SCRIPT ---
# --- Configuration ---
PROJECT_ID = "prj-hackathon-team2"
LOCATION = "europe-west4"
REASONING_ENGINE_ID = "1451073873687609344"

try:
    print("\n" + "="*50)
    print("INITIALIZING VERTEX AI SDK...")
    print("="*50 + "\n")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    print("\n" + "="*50)
    print(f"CONNECTING TO REASONING ENGINE: {REASONING_ENGINE_ID}...")
    print("="*50 + "\n")
    reasoning_engine = reasoning_engines.ReasoningEngine(REASONING_ENGINE_ID)

    print("\n" + "="*50)
    print("SENDING QUERY (THIS IS WHERE IT LIKELY HANGS)...")
    print("="*50 + "\n")
    response = reasoning_engine.stream_query(
        input="What are my benefits?"
    )

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