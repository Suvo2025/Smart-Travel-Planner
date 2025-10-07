import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_weather(city):
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        if "list" not in data:
            return {"error": "City not found"}

        # Extract next 3 days forecast
        forecast = []
        for entry in data["list"][:8]:  # Get more entries for better coverage
            forecast.append({
                "datetime": entry["dt_txt"],
                "temp": entry["main"]["temp"],
                "condition": entry["weather"][0]["description"]
            })
        return forecast
    except requests.exceptions.RequestException as e:
        print(f"Weather API Error: {e}")
        return {"error": "Failed to fetch weather data"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "An unexpected error occurred"}