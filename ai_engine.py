import time
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable")

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_ai_coaching(df):
    if df.empty:
        return "Track habits for a few days to receive AI coaching."

    recent_data = df.tail(7).to_string(index=False)

    prompt = f"""
    You are a high-performance productivity coach.
    Analyze this user's 7-day habit tracking data. 
    Provide 3 very concise, actionable improvement suggestions based solely on this data.
    Keep the tone professional and motivating.
    
    Data:
    {recent_data}
    """

    # Retry logic parameters
    max_retries = 3
    base_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt]
            )
            return response.text
            
        except Exception as e:
            error_str = str(e)
            
            # Check if the error is a 503
            if "503" in error_str:
                if attempt < max_retries - 1:
                    # Calculate backoff time (2s, then 4s, etc.)
                    sleep_time = base_delay * (2 ** attempt)
                    print(f"Server busy (503). Retrying in {sleep_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(sleep_time)
                    continue # Try the loop again
                else:
                    return "The AI coaching servers are currently too busy. Please try again in a few minutes."
            else:
                # If it's a different error (like an invalid API key), don't retry, just fail gracefully.
                print(f"API Error: {e}")
                return "AI coaching is temporarily unavailable due to a connection issue."