// Smart Travel Planner Script - Complete Version with Fixed Language Support
document.addEventListener("DOMContentLoaded", () => {
  console.log('🚀 Smart Travel Planner initialized');
  
  // Make title clickable to reload page
  const title = document.querySelector('.clickable-title');
  if (title) {
    title.style.cursor = 'pointer';
    title.title = 'Click to refresh page and start over';
    title.addEventListener('click', function() {
      console.log('Reloading page...');
      location.reload();
    });
  }

  const form = document.getElementById("travelForm");
  const destinationInput = document.getElementById("destinationInput");
  const startDateInput = document.getElementById("startDate");
  const endDateInput = document.getElementById("endDate");
  const daysInput = document.getElementById("daysInput");
  const preferencesInput = document.getElementById("preferencesInput");
  
  const loading = document.getElementById("loading");
  const result = document.getElementById("result");
  const errorMessage = document.getElementById("errorMessage");
  const errorText = document.getElementById("errorText");
  
  const weatherData = document.getElementById("weatherData");
  const seasonalData = document.getElementById("seasonalData");
  const itineraryData = document.getElementById("itineraryData");

  // Set minimum date to today
  const today = new Date();
  const todayFormatted = today.toISOString().split('T')[0];
  startDateInput.min = todayFormatted;
  endDateInput.min = todayFormatted;

  // Set default dates
  startDateInput.value = todayFormatted;

  // Set default end date to 2 days from start (3 days total)
  const defaultEndDate = new Date(today);
  defaultEndDate.setDate(today.getDate() + 2);
  endDateInput.value = defaultEndDate.toISOString().split('T')[0];

  // Calculate initial days
  calculateDays();

  // Calculate days when dates change
  startDateInput.addEventListener('change', function() {
    if (startDateInput.value && endDateInput.value) {
      const start = new Date(startDateInput.value);
      const end = new Date(endDateInput.value);
      
      if (end < start) {
        endDateInput.value = startDateInput.value;
      }
      calculateDays();
    }
  });

  endDateInput.addEventListener('change', function() {
    if (startDateInput.value && endDateInput.value) {
      const start = new Date(startDateInput.value);
      const end = new Date(endDateInput.value);
      
      if (end < start) {
        showError("End date cannot be before start date. Adjusting...");
        endDateInput.value = startDateInput.value;
      }
      calculateDays();
    }
  });

  function calculateDays() {
    if (startDateInput.value && endDateInput.value) {
      const start = new Date(startDateInput.value);
      const end = new Date(endDateInput.value);
      
      const timeDiff = end.getTime() - start.getTime();
      const days = Math.ceil(timeDiff / (1000 * 3600 * 24)) + 1;
      
      console.log(`Start: ${startDateInput.value}, End: ${endDateInput.value}, Days: ${days}`);
      
      if (days > 0 && days <= 30) {
        daysInput.value = days;
        errorMessage.classList.add('hidden');
      } else if (days > 30) {
        daysInput.value = 30;
        showError("Maximum trip duration is 30 days. Please adjust your dates.");
      } else {
        daysInput.value = 1;
        showError("End date must be after start date.");
      }
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const destination = destinationInput.value.trim();
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;
    const days = parseInt(daysInput.value);
    const preferences = preferencesInput.value;

    if (!destination) {
      showError("Please enter a destination!");
      return;
    }

    if (!startDate || !endDate) {
      showError("Please select both start and end dates!");
      return;
    }

    if (days < 1 || days > 30) {
      showError("Please select a trip duration between 1 and 30 days.");
      return;
    }

    console.log(`Submitting: ${destination}, ${days} days, ${startDate} to ${endDate}`);

    loading.classList.remove('hidden');
    result.style.display = 'none';
    errorMessage.classList.add('hidden');

    try {
      const response = await fetch(
        `/api/plan_trip?destination=${encodeURIComponent(destination)}&days=${days}&preferences=${encodeURIComponent(preferences)}&start_date=${startDate}`
      );
      
      const data = await response.json();

      if (response.ok) {
        displayResults(data);
      } else {
        showError(data.detail || "Unable to create travel plan. Please try another destination.");
      }
    } catch (error) {
      console.error("Fetch error:", error);
      showError("Failed to connect to server. Please check your connection and try again.");
    } finally {
      loading.classList.add('hidden');
    }
  });

  function displayResults(data) {
    console.log('📊 Displaying results for:', data.destination);
    
    // Display weather data
    weatherData.innerHTML = "";
    if (data.weather && Array.isArray(data.weather)) {
      const weatherByDate = {};
      data.weather.forEach(w => {
        const date = w.datetime.split(" ")[0];
        if (!weatherByDate[date]) {
          weatherByDate[date] = w;
        }
      });

      Object.values(weatherByDate).slice(0, 5).forEach(w => {
        const weatherItem = document.createElement("div");
        weatherItem.className = "weather-item";
        
        const date = new Date(w.datetime);
        const dateStr = date.toLocaleDateString('en-US', { 
          weekday: 'short', 
          month: 'short', 
          day: 'numeric' 
        });

        weatherItem.innerHTML = `
          <div class="weather-date">${dateStr}</div>
          <div class="weather-temp">${Math.round(w.temp)}°C</div>
          <div class="weather-condition">${w.condition}</div>
        `;
        weatherData.appendChild(weatherItem);
      });
    }

    displaySeasonalInfo(data.start_date, data.destination, data.days);
    displayLanguageAndCultureTips(data.destination, data.preferences);
    itineraryData.textContent = data.itinerary;

    result.style.display = 'block';
    result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function displaySeasonalInfo(startDate, destination, days) {
    if (!startDate) return;
    
    const travelDate = new Date(startDate);
    const month = travelDate.getMonth();
    const season = getSeason(month);
    const monthName = travelDate.toLocaleDateString('en-US', { month: 'long' });
    
    const seasonalInfo = `
🌤️ Travel Season: ${season} (${monthName})
📅 Trip Duration: ${days} days

📅 Best Activities:
• ${getSeasonalActivities(season, destination)}

🎉 Seasonal Events:
• ${getSeasonalEvents(season, destination)}

👕 Packing Tips:
• ${getPackingTips(season)}

🍽️ Seasonal Foods:
• ${getSeasonalFoods(season, destination)}
    `;
    
    seasonalData.textContent = seasonalInfo;
  }

  function displayLanguageAndCultureTips(destination, preferences) {
    displayLanguagePhrases(destination);
    displayCulturalEtiquette(destination);
    displayFoodCulture(destination, preferences);
    displayPracticalTips(destination);
    initCultureTabs();
  }

  function displayLanguagePhrases(destination) {
    const phrases = generateLanguagePhrases(destination);
    let phrasesHTML = '';
    
    phrases.forEach(phrase => {
      phrasesHTML += `
        <div class="language-phrase">
          <div class="phrase-row">
            <div class="phrase-english">${phrase.english}</div>
            <div class="phrase-local">${phrase.local}</div>
          </div>
          <div class="phrase-pronunciation">${phrase.pronunciation}</div>
        </div>
      `;
    });
    
    document.getElementById('languageData').innerHTML = phrasesHTML;
  }

  function displayCulturalEtiquette(destination) {
    const etiquette = generateCulturalEtiquette(destination);
    let etiquetteHTML = '';
    
    etiquette.forEach(tip => {
      etiquetteHTML += `
        <div class="etiquette-tip">
          <div class="tip-title">${tip.title}</div>
          <div class="tip-content">${tip.content}</div>
        </div>
      `;
    });
    
    document.getElementById('etiquetteData').innerHTML = etiquetteHTML;
  }

  function displayFoodCulture(destination, preferences) {
    const foodTips = generateFoodCulture(destination, preferences);
    let foodHTML = '';
    
    foodTips.forEach(tip => {
      foodHTML += `
        <div class="food-tip">
          <div class="tip-title">${tip.title}</div>
          <div class="tip-content">${tip.content}</div>
        </div>
      `;
    });
    
    document.getElementById('foodData').innerHTML = foodHTML;
  }

  function displayPracticalTips(destination) {
    const tips = generatePracticalTips(destination);
    let tipsHTML = '';
    
    tips.forEach(tip => {
      tipsHTML += `
        <div class="general-tip">
          <div class="tip-title">${tip.title}</div>
          <div class="tip-content">${tip.content}</div>
        </div>
      `;
    });
    
    document.getElementById('tipsData').innerHTML = tipsHTML;
  }

  function initCultureTabs() {
    const tabs = document.querySelectorAll('.culture-tab');
    
    tabs.forEach(tab => {
      tab.addEventListener('click', function() {
        tabs.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        
        document.querySelectorAll('.tab-content').forEach(content => {
          content.classList.remove('active');
        });
        
        const tabName = this.getAttribute('data-tab');
        document.getElementById(tabName + 'Content').classList.add('active');
      });
    });
  }

  function getSeason(month) {
    if (month >= 2 && month <= 4) return "Spring 🌸";
    if (month >= 5 && month <= 7) return "Summer ☀️";
    if (month >= 8 && month <= 10) return "Autumn 🍂";
    return "Winter ❄️";
  }

  function getSeasonalActivities(season, destination) {
    const activities = {
      "Spring 🌸": "Perfect for outdoor sightseeing, garden visits, and spring festivals",
      "Summer ☀️": "Great for beach activities, hiking, and outdoor adventures",
      "Autumn 🍂": "Ideal for cultural tours, wine tasting, and fall foliage viewing",
      "Winter ❄️": "Perfect for indoor museums, winter sports, and cozy experiences"
    };
    return activities[season] || "Enjoy various activities based on your preferences";
  }

  function getSeasonalEvents(season, destination) {
    const events = {
      "Spring 🌸": "Spring festivals, flower shows, cultural events",
      "Summer ☀️": "Summer concerts, outdoor markets, local celebrations",
      "Autumn 🍂": "Harvest festivals, cultural events, holiday preparations",
      "Winter ❄️": "Winter markets, holiday celebrations, New Year events"
    };
    return events[season] || "Check local event calendars for current activities";
  }

  function getPackingTips(season) {
    const tips = {
      "Spring 🌸": "Light layers, rain jacket, comfortable walking shoes",
      "Summer ☀️": "Light clothing, sunscreen, hat, sunglasses",
      "Autumn 🍂": "Warm layers, waterproof jacket, comfortable boots",
      "Winter ❄️": "Heavy coat, warm layers, gloves, scarf, thermal wear"
    };
    return tips[season] || "Pack according to weather forecast and planned activities";
  }

  function getSeasonalFoods(season, destination) {
    const foods = {
      "Spring 🌸": "Fresh produce, spring vegetables, light seasonal dishes",
      "Summer ☀️": "Fresh fruits, salads, grilled foods, refreshing drinks",
      "Autumn 🍂": "Harvest vegetables, warm soups, seasonal fruits",
      "Winter ❄️": "Comfort foods, warm drinks, holiday specialties"
    };
    return foods[season] || "Try local seasonal specialties and traditional dishes";
  }

  // FIXED LANGUAGE FUNCTIONS WITH REAL DATA
  function generateLanguagePhrases(destination) {
    const languageData = getLanguageDataForDestination(destination);
    return languageData.phrases;
  }

  function getLanguageDataForDestination(destination) {
    const destLower = destination.toLowerCase();
    
    // Language data for popular destinations
    const languageDatabase = {
      'france': {
        language: 'French',
        phrases: [
          { english: "Hello", local: "Bonjour", pronunciation: "bohn-zhoor" },
          { english: "Thank you", local: "Merci", pronunciation: "mehr-see" },
          { english: "Please", local: "S'il vous plaît", pronunciation: "seel voo play" },
          { english: "Excuse me", local: "Excusez-moi", pronunciation: "ex-koo-zay mwah" },
          { english: "How much?", local: "Combien?", pronunciation: "kohm-byen" },
          { english: "Where is...?", local: "Où est...?", pronunciation: "oo ay" },
          { english: "I need help", local: "J'ai besoin d'aide", pronunciation: "zhay buh-swahn ded" },
          { english: "Goodbye", local: "Au revoir", pronunciation: "oh ruh-vwahr" }
        ]
      },
      'spain': {
        language: 'Spanish',
        phrases: [
          { english: "Hello", local: "Hola", pronunciation: "oh-lah" },
          { english: "Thank you", local: "Gracias", pronunciation: "grah-see-ahs" },
          { english: "Please", local: "Por favor", pronunciation: "por fah-vor" },
          { english: "Excuse me", local: "Perdón", pronunciation: "pehr-dohn" },
          { english: "How much?", local: "¿Cuánto cuesta?", pronunciation: "kwahn-toh kwehs-tah" },
          { english: "Where is...?", local: "¿Dónde está...?", pronunciation: "dohn-deh ehs-tah" },
          { english: "I need help", local: "Necesito ayuda", pronunciation: "neh-seh-see-toh ah-yoo-dah" },
          { english: "Goodbye", local: "Adiós", pronunciation: "ah-dee-ohs" }
        ]
      },
      'italy': {
        language: 'Italian',
        phrases: [
          { english: "Hello", local: "Ciao", pronunciation: "chow" },
          { english: "Thank you", local: "Grazie", pronunciation: "graht-see-eh" },
          { english: "Please", local: "Per favore", pronunciation: "pehr fah-voh-reh" },
          { english: "Excuse me", local: "Scusi", pronunciation: "skoo-zee" },
          { english: "How much?", local: "Quanto costa?", pronunciation: "kwahn-toh koh-stah" },
          { english: "Where is...?", local: "Dove è...?", pronunciation: "doh-veh eh" },
          { english: "I need help", local: "Ho bisogno di aiuto", pronunciation: "oh bee-zohn-yoh dee ah-yoo-toh" },
          { english: "Goodbye", local: "Arrivederci", pronunciation: "ah-ree-veh-dehr-chee" }
        ]
      },
      'japan': {
        language: 'Japanese',
        phrases: [
          { english: "Hello", local: "こんにちは", pronunciation: "kon-nichi-wa" },
          { english: "Thank you", local: "ありがとう", pronunciation: "ah-ree-gah-toh" },
          { english: "Please", local: "お願いします", pronunciation: "oh-ne-gai-shi-mas" },
          { english: "Excuse me", local: "すみません", pronunciation: "soo-mee-mah-sen" },
          { english: "How much?", local: "いくらですか？", pronunciation: "ee-koo-rah des-ka" },
          { english: "Where is...?", local: "...はどこですか？", pronunciation: "...wah do-ko des-ka" },
          { english: "I need help", local: "助けてください", pronunciation: "tah-skeh-teh koo-dah-sai" },
          { english: "Goodbye", local: "さようなら", pronunciation: "sah-yoh-nah-rah" }
        ]
      },
      'germany': {
        language: 'German',
        phrases: [
          { english: "Hello", local: "Hallo", pronunciation: "hah-loh" },
          { english: "Thank you", local: "Danke", pronunciation: "dahn-keh" },
          { english: "Please", local: "Bitte", pronunciation: "bit-teh" },
          { english: "Excuse me", local: "Entschuldigung", pronunciation: "ent-shool-dee-goong" },
          { english: "How much?", local: "Wie viel?", pronunciation: "vee feel" },
          { english: "Where is...?", local: "Wo ist...?", pronunciation: "voh ist" },
          { english: "I need help", local: "Ich brauche Hilfe", pronunciation: "ish brow-che hil-fe" },
          { english: "Goodbye", local: "Auf Wiedersehen", pronunciation: "owf vee-der-zayn" }
        ]
      },
      'china': {
        language: 'Mandarin Chinese',
        phrases: [
          { english: "Hello", local: "你好", pronunciation: "nee how" },
          { english: "Thank you", local: "谢谢", pronunciation: "shyeh-shyeh" },
          { english: "Please", local: "请", pronunciation: "ching" },
          { english: "Excuse me", local: "对不起", pronunciation: "way dway" },
          { english: "How much?", local: "多少钱？", pronunciation: "dwoh shao chyen" },
          { english: "Where is...?", local: "...在哪里？", pronunciation: "...dzai nah lee" },
          { english: "I need help", local: "我需要帮助", pronunciation: "wo shoo yow bang joo" },
          { english: "Goodbye", local: "再见", pronunciation: "dzai jyen" }
        ]
      },
      'india': {
        language: 'Hindi',
        phrases: [
          { english: "Hello", local: "नमस्ते", pronunciation: "nuh-muh-stay" },
          { english: "Thank you", local: "धन्यवाद", pronunciation: "dhun-yuh-vaad" },
          { english: "Please", local: "कृपया", pronunciation: "krip-yaa" },
          { english: "Excuse me", local: "माफ़ कीजिए", pronunciation: "maaf keejiye" },
          { english: "How much?", local: "कितना?", pronunciation: "kit-naa" },
          { english: "Where is...?", local: "...कहाँ है?", pronunciation: "...kahaan hai" },
          { english: "I need help", local: "मुझे मदद चाहिए", pronunciation: "mujhe madad chaahiye" },
          { english: "Goodbye", local: "अलविदा", pronunciation: "al-vi-daa" }
        ]
      },
      'default': {
        language: 'Local Language',
        phrases: [
          { english: "Hello", local: "Learn local greeting", pronunciation: "Smile and be friendly" },
          { english: "Thank you", local: "Learn local phrase", pronunciation: "Show appreciation" },
          { english: "Please", local: "Learn local phrase", pronunciation: "Be polite" },
          { english: "Excuse me", local: "Learn local phrase", pronunciation: "Get attention politely" },
          { english: "How much?", local: "Learn local phrase", pronunciation: "Point and show numbers" },
          { english: "Where is...?", local: "Learn local phrase", pronunciation: "Use maps and gestures" },
          { english: "I need help", local: "Learn local phrase", pronunciation: "Find tourist information" },
          { english: "Goodbye", local: "Learn local phrase", pronunciation: "Wave and smile" }
        ]
      }
    };

    // Find matching language data
    for (const [country, data] of Object.entries(languageDatabase)) {
      if (destLower.includes(country)) {
        return data;
      }
    }
    
    return languageDatabase.default;
  }

  function generateCulturalEtiquette(destination) {
    const languageData = getLanguageDataForDestination(destination);
    
    const etiquetteData = {
      'france': [
        { title: "Greetings", content: "Greet with 'Bonjour' and handshake. Use 'Monsieur'/'Madame' formally." },
        { title: "Dining", content: "Keep hands on table (not lap). Say 'Bon appétit' before eating." },
        { title: "Tipping", content: "Service included. Round up bill or leave 5-10% for excellent service." },
        { title: "Personal Space", content: "Cheek kissing common among friends (2-4 kisses depending on region)." }
      ],
      'spain': [
        { title: "Greetings", content: "Handshakes for business, cheek kisses for friends and family." },
        { title: "Dining", content: "Late meals: lunch 2-4 PM, dinner 9-11 PM. Don't rush meals." },
        { title: "Tipping", content: "Not mandatory. Round up bill or leave 5-10% in restaurants." },
        { title: "Personal Space", content: "Physical contact common. Loud conversations normal in social settings." }
      ],
      'italy': [
        { title: "Greetings", content: "Cheek kisses common. Use formal titles until invited to use first names." },
        { title: "Dining", content: "No cappuccino after 11 AM. Don't ask for cheese with seafood pasta." },
        { title: "Tipping", content: "Service often included. Round up or leave 1-2 euros per person." },
        { title: "Personal Space", content: "Close talking distance common. Expressive hand gestures normal." }
      ],
      'japan': [
        { title: "Greetings", content: "Bow when greeting. Business cards exchanged with both hands." },
        { title: "Dining", content: "Say 'itadakimasu' before eating. Don't stick chopsticks upright in rice." },
        { title: "Tipping", content: "Not customary. May be considered rude. Excellent service is standard." },
        { title: "Personal Space", content: "Respect personal space. Quiet in public spaces. Remove shoes indoors." }
      ],
      'germany': [
        { title: "Greetings", content: "Firm handshake with eye contact. Use formal titles until invited otherwise." },
        { title: "Dining", content: "Punctuality important. Keep hands visible on table. Say 'Guten Appetit'." },
        { title: "Tipping", content: "Round up to nearest euro or add 5-10%. Tell server the total including tip." },
        { title: "Personal Space", content: "Respect personal space. Direct communication valued." }
      ],
      'default': [
        { title: "Greetings", content: "Research local greeting customs. Handshakes usually safe for business." },
        { title: "Dining", content: "Observe local dining times and customs. Follow host's lead." },
        { title: "Tipping", content: "Research local tipping customs. Some cultures find tipping offensive." },
        { title: "Personal Space", content: "Observe personal distance. Some cultures stand closer when talking." }
      ]
    };

    for (const [country, data] of Object.entries(etiquetteData)) {
      if (destination.toLowerCase().includes(country)) {
        return data;
      }
    }
    return etiquetteData.default;
  }

  function generateFoodCulture(destination, preferences) {
    const foodData = {
      'france': [
        { title: "Local Specialties", content: "Croissants, baguettes, cheese, wine, coq au vin, ratatouille" },
        { title: "Dining Times", content: "Breakfast: 7-9 AM, Lunch: 12-2 PM, Dinner: 7-9 PM" },
        { title: "Street Food", content: "Crêpes, galettes, croque-monsieur, falafel (in Paris)" },
        { title: "Dietary Customs", content: "Bread served with meals. Cheese course after main, before dessert." }
      ],
      'spain': [
        { title: "Local Specialties", content: "Paella, tapas, jamón ibérico, gazpacho, churros con chocolate" },
        { title: "Dining Times", content: "Late meals: Lunch 2-4 PM, Dinner 9-11 PM, Tapas: 6-9 PM" },
        { title: "Street Food", content: "Churros, bocadillos, empanadas, fried fish" },
        { title: "Dietary Customs", content: "Tapas culture - small plates shared. Siesta break common." }
      ],
      'italy': [
        { title: "Local Specialties", content: "Pizza, pasta, gelato, espresso, risotto, prosciutto" },
        { title: "Dining Times", content: "Breakfast: 7-10 AM, Lunch: 1-3 PM, Dinner: 8-10 PM" },
        { title: "Street Food", content: "Pizza al taglio, arancini, panini, supplì" },
        { title: "Dietary Customs", content: "Coffee culture - cappuccino only in morning. Pasta as first course." }
      ],
      'japan': [
        { title: "Local Specialties", content: "Sushi, ramen, tempura, yakitori, okonomiyaki, takoyaki" },
        { title: "Dining Times", content: "Breakfast: 7-9 AM, Lunch: 12-1 PM, Dinner: 6-8 PM" },
        { title: "Street Food", content: "Takoyaki, taiyaki, yakitori, okonomiyaki at festivals" },
        { title: "Dietary Customs", content: "Say 'itadakimasu' before eating. Slurping noodles shows enjoyment." }
      ],
      'default': [
        { title: "Local Specialties", content: "Research regional dishes and traditional cuisine before traveling" },
        { title: "Dining Times", content: "Check local meal times as they may differ from your home country" },
        { title: "Street Food", content: "Look for busy vendors with high turnover for fresh, safe options" },
        { title: "Dietary Customs", content: "Research any food restrictions or dining etiquette specific to region" }
      ]
    };

    for (const [country, data] of Object.entries(foodData)) {
      if (destination.toLowerCase().includes(country)) {
        return data;
      }
    }
    return foodData.default;
  }

  function generatePracticalTips(destination) {
    const languageData = getLanguageDataForDestination(destination);
    
    return [
      { 
        title: "Transportation", 
        content: `Research local transport options. Learn phrases like 'Where is the metro/bus station?' in ${languageData.language}` 
      },
      { 
        title: "Money & Currency", 
        content: "Check local currency. Have small bills for markets. Notify your bank of travel plans." 
      },
      { 
        title: "Safety", 
        content: "Keep valuables secure. Know emergency numbers. Be aware of common tourist scams." 
      },
      { 
        title: "Communication", 
        content: `Learn basic ${languageData.language} phrases. Download translation app. Get local SIM card if needed.` 
      }
    ];
  }

  function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove("hidden");
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
});

console.log('✅ script.js loaded successfully');