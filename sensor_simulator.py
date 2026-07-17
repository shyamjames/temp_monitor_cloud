import os
import time
import random
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    exit(1)

supabase: Client = create_client(url, key)

def simulate_sensor():
    print("Starting sensor simulation. Press Ctrl+C to stop.")
    try:
        while True:
            # Generate random temperature between 20.0 and 40.0
            temp = round(random.uniform(20.0, 40.0), 2)
            
            # Get current date and time
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")
            
            # Prepare data
            data, count = supabase.table("temperature_readings").insert({
                "temperature": temp,
                "date": current_date,
                "time": current_time
            }).execute()
            
            print(f"Temperature: {temp}°C | Time: {current_time} | Uploaded Successfully")
            
            # Wait for 5 seconds before next reading
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nSensor simulation stopped cleanly.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    simulate_sensor()
