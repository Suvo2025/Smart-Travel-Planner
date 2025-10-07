from fastapi import APIRouter, Query, HTTPException
from services.weather import get_weather
from services.ai_itinerary import generate_itinerary

router = APIRouter()

@router.get("/get_weather")
def get_weather_route(
    city: str = Query(..., description="City name")
):
    """
    Returns current weather + Gemini summary for a city
    """
    try:
        weather_data = get_weather(city)

        # Check if weather API returned an error
        if isinstance(weather_data, dict) and "error" in weather_data:
            raise HTTPException(status_code=404, detail=weather_data["error"])

        # Generate AI summary
        summary = generate_itinerary(city, 1, "general weather insights", weather_data)

        return {
            "city": city,
            "temperature": round(weather_data[0]["temp"], 1),
            "condition": weather_data[0]["condition"],
            "gemini_summary": summary
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_weather_route: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/plan_trip")
def plan_trip(
    destination: str = Query(..., description="City name"),
    days: int = Query(3, description="Number of days"),
    preferences: str = Query("sightseeing, food, culture", description="User travel preferences"),
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)")
):
    """
    Generate AI-based travel itinerary with weather forecast and seasonal recommendations
    """
    try:
        print(f"Plan trip called: {destination}, {days} days, {preferences}, start_date: {start_date}")
        
        # Validate days parameter
        if days < 1 or days > 30:
            raise HTTPException(status_code=400, detail="Trip duration must be between 1 and 30 days")
        
        weather_data = get_weather(destination)
        
        if isinstance(weather_data, dict) and "error" in weather_data:
            print(f"Weather error: {weather_data['error']}")
            raise HTTPException(status_code=404, detail=weather_data["error"])
        
        print(f"Generating itinerary for {days} days in {destination}...")
        itinerary = generate_itinerary(destination, days, preferences, weather_data, start_date)
        print(f"Successfully generated {days}-day itinerary for {destination}")
        
        return {
            "destination": destination,
            "days": days,
            "preferences": preferences,
            "start_date": start_date,
            "weather": weather_data,
            "itinerary": itinerary
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in plan_trip: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")