import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in .env file")
    genai_configured = False
else:
    try:
        genai.configure(api_key=api_key)
        genai_configured = True
        print("Gemini API configured successfully")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        genai_configured = False

def get_correct_model():
    """
    Use the exact model names from your available list
    """
    # From your console output, these models are available:
    correct_models = [
        'models/gemini-2.0-flash',  # This should work
        'models/gemini-2.0-flash-001',
        'models/gemini-2.0-flash-exp',
        'models/gemini-pro-latest',
        'models/gemini-2.5-flash',
    ]
    
    for model_name in correct_models:
        try:
            # Test the model
            model = genai.GenerativeModel(model_name)
            print(f"✅ Model {model_name} is available and working")
            return model_name
        except Exception as e:
            print(f"❌ Model {model_name} failed: {str(e)[:100]}...")
            continue
    
    print("❌ No working models found from the list")
    return None

def generate_itinerary(destination, days, preferences, weather_data, start_date=None):
    """
    Generate a detailed travel itinerary for ANY city worldwide
    """
    try:
        if not genai_configured:
            print("Gemini API not configured, using universal detailed fallback")
            return generate_universal_detailed_itinerary(destination, days, preferences, weather_data, start_date)
        
        # Check if weather_data has an error
        if isinstance(weather_data, dict) and "error" in weather_data:
            weather_summary = "Weather data unavailable"
        else:
            # Create weather summary from forecast
            weather_summary = "\n".join([
                f"- {w['datetime']}: {w['condition']}, {w['temp']}°C" 
                for w in weather_data[:5] if 'condition' in w
            ])
        
        # Add seasonal information if start_date is provided
        seasonal_info = ""
        if start_date:
            try:
                travel_date = datetime.strptime(start_date, "%Y-%m-%d")
                month = travel_date.month
                season = get_season(month)
                seasonal_info = f"\n**Travel Season:** {season} (Month: {travel_date.strftime('%B')})"
            except:
                seasonal_info = "\n**Travel Season:** Information unavailable"
        
        prompt = f"""
You are an expert local travel guide for {destination}. Create a detailed {days}-day itinerary focusing on {preferences}.

**CRITICAL REQUIREMENTS:**
1. Use ONLY real, existing locations in {destination}
2. Include specific street names, neighborhoods, and districts
3. Mention actual restaurants, cafes, and their specialties
4. Include real landmarks, museums, parks with exact names
5. Provide practical transportation details between locations
6. Suggest specific local dishes and where to find them
7. Include realistic timing and duration for each activity
8. Consider geographic logic - group nearby attractions

**Destination:** {destination}
**Duration:** {days} days
**Interests:** {preferences}
**Weather:** {weather_summary}
{seasonal_info}

**FORMAT EACH DAY LIKE THIS:**

**DAY [X]: [SPECIFIC THEME/AREA]**

🌅 **MORNING (8:00 AM - 12:00 PM):**
- **[ACTUAL LANDMARK NAME]** - [Exact street/neighborhood]
  - Specific activities and highlights
  - Duration: X hours | Cost: if any
- **[ACTUAL ATTRACTION NAME]** - [Exact location]
  - What to see/experience

🍽️ **LUNCH (12:00 PM - 1:30 PM):**
- **[ACTUAL RESTAURANT NAME]** - [Street/area]
  - Must-try dishes: [Specific menu items]
  - Price range: [Budget/Mid-range/Luxury]

🏛️ **AFTERNOON (1:30 PM - 5:00 PM):**
- **[ACTUAL ATTRACTION NAME]** - [Exact location]
  - Transportation from previous location
  - Duration and highlights
- **[ACTUAL SITE NAME]** - [Neighborhood]

🌃 **EVENING (6:00 PM - 9:00 PM):**
- **[ACTUAL RESTAURANT/VENUE]** - [Location]
  - Evening activities or dining
  - Reservation requirements if any

**ADD THESE SECTIONS AT THE END:**

**MUST-TRY LOCAL FOODS:**
- [Dish 1] at [Specific restaurant/area]
- [Dish 2] at [Specific restaurant/area]

**TRANSPORTATION TIPS:**
- Best areas to stay
- Public transport options
- Walking routes

**BUDGET ESTIMATE:**
- Accommodation ranges
- Food costs per day
- Activity expenses

**LOCAL CUSTOMS:**
- Cultural etiquette
- Dress codes if any
- Tipping customs

IMPORTANT: All locations must be REAL and actually exist in {destination}. No made-up places.
"""

        print(f"Generating AI itinerary for {days} days in {destination}")
        
        # Get the correct model
        model_name = get_correct_model()
        if not model_name:
            print("No working models found, using universal detailed fallback")
            return generate_universal_detailed_itinerary(destination, days, preferences, weather_data, start_date)
        
        print(f"Using model: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        print(f"✅ Successfully generated {days}-day itinerary for {destination}")
        return response.text
        
    except Exception as e:
        print(f"❌ AI generation failed: {e}")
        print("Using universal detailed fallback itinerary")
        return generate_universal_detailed_itinerary(destination, days, preferences, weather_data, start_date)

def get_season(month):
    """Determine season based on month"""
    if month in [12, 1, 2]:
        return "Winter ❄️"
    elif month in [3, 4, 5]:
        return "Spring 🌸"
    elif month in [6, 7, 8]:
        return "Summer ☀️"
    else:
        return "Autumn 🍂"

def generate_universal_detailed_itinerary(destination, days, preferences, weather_data, start_date=None):
    """
    Generate a smart, detailed itinerary for ANY city worldwide
    """
    print(f"Creating universal detailed itinerary for {days} days in {destination}")
    
    seasonal_info = ""
    if start_date:
        try:
            travel_date = datetime.strptime(start_date, "%Y-%m-%d")
            month = travel_date.month
            season = get_season(month)
            seasonal_info = f"\n🌤️ Travel Season: {season}"
        except:
            seasonal_info = ""
    
    weather_info = ""
    if weather_data and not isinstance(weather_data, dict):
        avg_temp = sum([w['temp'] for w in weather_data[:3]]) / 3
        conditions = [w['condition'] for w in weather_data[:3]]
        weather_info = f"\n🌤️ Weather: {avg_temp:.1f}°C, {', '.join(set(conditions))}"
    
    # Get smart itinerary based on preferences and destination type
    detailed_content = generate_smart_universal_itinerary(destination, days, preferences)
    
    itinerary = f"""
🗺️ {days}-Day Travel Plan for {destination}
{seasonal_info}{weather_info}

Travel Style: {preferences}

{detailed_content}

💡 **Travel Planning Tips for {destination}:**

**To Get Specific Locations:**
• Use Google Maps to find restaurants near major attractions
• Check TripAdvisor for top-rated local eateries
• Visit official tourism websites for current information
• Ask hotel concierge for local recommendations

**Research Tools:**
• Google Maps: For exact addresses and directions
• TripAdvisor: For restaurant reviews and ratings
• Official tourism websites: For current hours and prices
• Travel blogs: For recent visitor experiences
"""
    
    return itinerary

def generate_smart_universal_itinerary(destination, days, preferences):
    """
    Generate intelligent itinerary for ANY city based on destination type and preferences
    """
    
    # Analyze preferences to customize the itinerary
    has_adventure = any(word in preferences.lower() for word in ['adventure', 'hiking', 'outdoor', 'trekking'])
    has_culture = any(word in preferences.lower() for word in ['culture', 'historical', 'heritage', 'museum'])
    has_food = any(word in preferences.lower() for word in ['food', 'cuisine', 'restaurant', 'culinary'])
    has_relaxation = any(word in preferences.lower() for word in ['relax', 'beach', 'spa', 'wellness'])
    has_shopping = any(word in preferences.lower() for word in ['shopping', 'market', 'mall', 'boutique'])
    
    itinerary = ""
    
    for day in range(1, days + 1):
        if day == 1:
            # Day 1: Arrival and Orientation
            itinerary += f"""
**DAY 1: ARRIVAL & CITY ORIENTATION**

🌅 **MORNING (8:00 AM - 12:00 PM): ARRIVAL & SETTLEMENT**
• Arrive in {destination} and check into your accommodation
• Get local SIM card and currency exchange
• Familiarize yourself with the neighborhood
• Identify nearby restaurants and convenience stores

🍽️ **LUNCH (12:00 PM - 1:30 PM): LOCAL INTRODUCTION**
• Try a well-rated local restaurant near your accommodation
• Sample basic regional dishes to understand local cuisine
• Observe local dining customs and etiquette

🏛️ **AFTERNOON (1:30 PM - 5:00 PM): INITIAL EXPLORATION**
• Visit the main city center or central square
• Locate tourist information centers for maps and advice
• Identify public transportation hubs and routes
• Take a walking tour of immediate surroundings

🌃 **EVENING (6:00 PM - 9:00 PM): FIRST IMPRESSIONS**
• Dinner at a recommended local establishment
• Evening stroll through popular local areas
• Plan next day's activities based on initial observations
"""
        
        elif day == 2:
            # Day 2: Major Attractions based on preferences
            morning_activities = ""
            afternoon_activities = ""
            
            if has_culture:
                morning_activities = f"""
• Visit the most famous historical landmarks in {destination}
• Explore main museums or cultural heritage sites
• Learn about local history and significant events"""
                
                afternoon_activities = f"""
• Continue cultural exploration with additional sites
• Visit religious or architectural landmarks
• Explore local art galleries or cultural centers"""
            
            elif has_adventure:
                morning_activities = f"""
• Start with outdoor activities around {destination}
• Explore natural parks or hiking trails
• Adventure sports or physical activities"""
                
                afternoon_activities = f"""
• Continue with nature exploration
• Visit scenic viewpoints or natural wonders
• Outdoor photography and exploration"""
            
            else:  # General sightseeing
                morning_activities = f"""
• Visit iconic landmarks and must-see attractions
• Explore famous neighborhoods and districts
• Photography at key city viewpoints"""
                
                afternoon_activities = f"""
• Continue sightseeing at major attractions
• Explore different areas of the city
• Visit popular local gathering spots"""
            
            itinerary += f"""
**DAY 2: MAJOR ATTRACTIONS & LANDMARKS**

🌅 **MORNING (8:00 AM - 12:00 PM): KEY SIGHTSEEING**
{morning_activities}

🍽️ **LUNCH (12:00 PM - 1:30 PM): AUTHENTIC CUISINE**
• Traditional restaurant serving local specialties
• Try regional dishes unique to {destination}
• Experience local dining atmosphere

🏛️ **AFTERNOON (1:30 PM - 5:00 PM): CONTINUED EXPLORATION**
{afternoon_activities}

🌃 **EVENING (6:00 PM - 9:00 PM): LOCAL EXPERIENCES**
• Dinner featuring regional culinary specialties
• Evening entertainment or cultural performances
• Night markets or illuminated landmarks
"""
        
        elif day == 3:
            # Day 3: Specialized experiences based on preferences
            specialized_morning = ""
            specialized_afternoon = ""
            
            if has_food:
                specialized_morning = f"""
• Food market tour or culinary district exploration
• Cooking class or food tasting experience
• Visit local producers or specialty food shops"""
                
                specialized_afternoon = f"""
• Continue food exploration in different neighborhoods
• Street food tasting tour
• Visit famous local eateries or food institutions"""
            
            elif has_shopping:
                specialized_morning = f"""
• Explore main shopping districts in {destination}
• Visit local markets for crafts and souvenirs
• Boutique and specialty store exploration"""
                
                specialized_afternoon = f"""
• Continue shopping in different areas
• Visit shopping malls or commercial centers
• Local craft and artisan workshops"""
            
            elif has_relaxation:
                specialized_morning = f"""
• Visit parks, gardens, or peaceful areas
• Relaxation activities or spa experiences
• Scenic and tranquil location exploration"""
                
                specialized_afternoon = f"""
• Continue relaxation and leisure activities
• Visit beaches, lakes, or natural retreats
• Wellness and rejuvenation experiences"""
            
            else:  # Mixed experiences
                specialized_morning = f"""
• Explore different neighborhoods of {destination}
• Visit local markets and community areas
• Discover hidden gems off the main tourist trail"""
                
                specialized_afternoon = f"""
• Personalized activities based on your interests
• Return to favorite spots for deeper exploration
• Local experiences and interactions"""
            
            itinerary += f"""
**DAY 3: SPECIALIZED EXPERIENCES**

🌅 **MORNING (8:00 AM - 12:00 PM): FOCUSED EXPLORATION**
{specialized_morning}

🍽️ **LUNCH (12:00 PM - 1:30 PM): CULINARY ADVENTURE**
• Try new local dishes or street food specialties
• Visit food markets or local eateries
• Experience diverse local cuisine

🏛️ **AFTERNOON (1:30 PM - 5:00 PM): CONTINUED SPECIALIZATION**
{specialized_afternoon}

🌃 **EVENING (6:00 PM - 9:00 PM): UNIQUE EXPERIENCES**
• Special dinner at unique or highly-rated restaurant
• Evening activities matching your interests
• Local nightlife or cultural events
"""
        
        else:
            # Additional days - more specialized or relaxed
            if day == days:  # Last day
                itinerary += f"""
**DAY {day}: FINAL EXPLORATIONS & DEPARTURE PREPARATION**

🌅 **MORNING (8:00 AM - 12:00 PM): LAST OPPORTUNITIES**
• Visit any remaining must-see attractions
• Return to favorite spots for final experiences
• Last-minute souvenir shopping

🍽️ **LUNCH (12:00 PM - 1:30 PM): FAREWELL MEAL**
• Enjoy final local cuisine experiences
• Visit highly recommended restaurants missed earlier
• Try dishes you haven't experienced yet

🏛️ **AFTERNOON (1:30 PM - 5:00 PM): RELAXED FINALE**
• Leisurely activities and final explorations
• Visit parks, gardens, or relaxing spots
• Preparation for departure

🌃 **EVENING (6:00 PM - 9:00 PM): DEPARTURE**
• Special farewell dinner
• Final evening stroll and photography
• Travel to airport or departure point
"""
            else:  # Middle days
                itinerary += f"""
**DAY {day}: DEEPER EXPLORATION**

🌅 **MORNING (8:00 AM - 12:00 PM): EXPANDED HORIZONS**
• Explore less-visited areas of {destination}
• Visit specialized museums or attractions
• Local neighborhood immersion

🍽️ **LUNCH (12:00 PM - 1:30 PM): CONTINUED CULINARY JOURNEY**
• Try different types of local cuisine
• Explore food from various regions or cultures
• Restaurant hopping or food court exploration

🏛️ **AFTERNOON (1:30 PM - 5:00 PM): ENRICHING EXPERIENCES**
• Cultural workshops or local activities
• Guided tours or specialized experiences
• Personal interest exploration

🌃 **EVENING (6:00 PM - 9:00 PM): EVENING DELIGHTS**
• Dinner at different types of establishments
• Evening entertainment or shows
• Local social experiences
"""
    
    # Add destination-specific practical information
    itinerary += f"""

🎯 **PRACTICAL INFORMATION FOR {destination.upper()}:**

**General Travel Tips:**
• Research current entry requirements and visa needs
• Learn basic local greetings and phrases
• Download offline maps and translation apps
• Understand local customs and dress codes

**Based on Your Preferences:**
{get_preference_specific_tips(preferences)}

**Transportation Advice:**
• Research public transportation options before arrival
• Consider ride-sharing app availability
• Learn about taxi services and approximate costs
• Identify walking-friendly areas

**Budget Planning:**
• Research accommodation costs in different areas
• Estimate daily food expenses based on dining preferences
• Account for attraction entrance fees and activity costs
• Include transportation expenses in your budget

**Safety Considerations:**
• Identify safe neighborhoods for accommodation
• Learn emergency numbers and hospital locations
• Understand local safety norms and precautions
• Keep copies of important documents

**To Get Specific Location Details:**
• Use Google Maps to find exact addresses
• Check recent reviews on TripAdvisor
• Consult official tourism websites
• Ask locals for current recommendations
"""
    
    return itinerary

def get_preference_specific_tips(preferences):
    """Generate tips based on specific travel preferences"""
    tips = []
    
    if any(word in preferences.lower() for word in ['adventure', 'hiking', 'outdoor']):
        tips.extend([
            "• Research local hiking trails and difficulty levels",
            "• Check weather conditions for outdoor activities",
            "• Pack appropriate gear and clothing",
            "• Consider guided adventure tours for safety"
        ])
    
    if any(word in preferences.lower() for word in ['culture', 'historical', 'museum']):
        tips.extend([
            "• Check museum opening hours and special exhibitions",
            "• Research historical site entry requirements",
            "• Consider hiring local guides for deeper insights",
            "• Learn about local customs and etiquette"
        ])
    
    if any(word in preferences.lower() for word in ['food', 'cuisine', 'restaurant']):
        tips.extend([
            "• Research local food specialties and must-try dishes",
            "• Identify food markets and street food areas",
            "• Learn about dining customs and tipping practices",
            "• Consider food tours for comprehensive tasting"
        ])
    
    if any(word in preferences.lower() for word in ['shopping', 'market']):
        tips.extend([
            "• Research best shopping districts and market days",
            "• Learn about local crafts and specialty products",
            "• Understand bargaining customs if applicable",
            "• Check VAT refund procedures for tourists"
        ])
    
    if any(word in preferences.lower() for word in ['relax', 'beach', 'spa']):
        tips.extend([
            "• Research best beaches or relaxation spots",
            "• Check spa and wellness center reviews",
            "• Consider resort areas for comprehensive relaxation",
            "• Pack appropriate relaxation and beach gear"
        ])
    
    if not tips:  # Default tips if no specific preferences
        tips.extend([
            "• Balance sightseeing with relaxation time",
            "• Mix popular attractions with local experiences",
            "• Allow flexibility for spontaneous discoveries",
            "• Consider local festivals or events during your visit"
        ])
    
    return "\n".join(tips)

# Cultural context functions for language and culture tips
def generate_cultural_context(destination, preferences):
    """
    Generate language and cultural information for any destination
    """
    cultural_info = {
        "language_phrases": generate_base_phrases(destination),
        "cultural_tips": generate_cultural_tips(destination),
        "food_etiquette": generate_food_etiquette(destination, preferences),
        "practical_info": generate_practical_info(destination)
    }
    return cultural_info

def generate_base_phrases(destination):
    """Generate basic language phrases for the destination"""
    # This would integrate with a language API or database
    # For now, return generic structure
    return [
        {"english": "Hello", "local": "[Local greeting]", "pronunciation": "[Pronunciation]"},
        {"english": "Thank you", "local": "[Local phrase]", "pronunciation": "[Pronunciation]"},
        {"english": "Please", "local": "[Local phrase]", "pronunciation": "[Pronunciation]"},
        {"english": "Excuse me", "local": "[Local phrase]", "pronunciation": "[Pronunciation]"},
        {"english": "How much?", "local": "[Local phrase]", "pronunciation": "[Pronunciation]"},
        {"english": "Where is...?", "local": "[Local phrase]", "pronunciation": "[Pronunciation]"},
        {"english": "I need help", "local": "[Local phrase]", "pronunciation": "[Pronunciation]"},
        {"english": "Goodbye", "local": "[Local phrase]", "pronunciation": "[Pronunciation]"}
    ]

def generate_cultural_tips(destination):
    """Generate cultural etiquette tips"""
    return [
        "Research local greeting customs before arrival",
        "Be aware of appropriate dress codes for different settings",
        "Learn about personal space norms in the local culture",
        "Understand local customs around photography and privacy"
    ]

def generate_food_etiquette(destination, preferences):
    """Generate food-related cultural information"""
    tips = [
        "Try to learn basic dining etiquette before visiting restaurants",
        "Research local food specialties and must-try dishes",
        "Understand tipping customs for restaurants in the area"
    ]
    
    if 'food' in preferences.lower():
        tips.append("Consider taking a local food tour for authentic experiences")
    
    return tips

def generate_practical_info(destination):
    """Generate practical travel information"""
    return [
        "Check visa requirements well in advance of travel",
        "Research local transportation options and payment methods",
        "Learn about local emergency numbers and healthcare access",
        "Understand local currency and common payment methods"
    ]