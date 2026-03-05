"""Weather skill.

Get weather information for any location.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import urllib.request
import urllib.parse
import json


SKILL_INFO = {
    "name": "weather",
    "version": "1.0.0",
    "description": "Get weather information",
}


@dataclass
class WeatherInfo:
    """Weather information."""
    location: str
    temperature: str
    description: str
    humidity: str
    wind: str
    
    def __str__(self) -> str:
        return f"""Weather for {self.location}:
  Temperature: {self.temperature}
  Conditions: {self.description}
  Humidity: {self.humidity}
  Wind: {self.wind}"""


@dataclass
class ForecastDay:
    """Single day forecast."""
    date: str
    temperature_high: str
    temperature_low: str
    description: str
    
    def __str__(self) -> str:
        return f"{self.date}: {self.description}, {self.temperature_low} - {self.temperature_high}"


def get_weather(
    location: str,
    units: str = "metric",
) -> WeatherInfo:
    """
    Get current weather for a location.
    
    Uses wttr.in API (free, no key needed).
    
    Args:
        location: City name or coordinates
        units: "metric" or "imperial"
    
    Returns:
        WeatherInfo object
    """
    # Use wttr.in (free weather API)
    url = f"https://wttr.in/{urllib.parse.quote(location)}?format=j1"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        
        current = data.get("current_condition", [{}])[0]
        area = data.get("nearest_area", [{}])[0]
        
        location_name = area.get("areaName", [{}])[0].get("value", location)
        
        if units == "imperial":
            temp = f"{current.get('temp_F', 'N/A')}°F"
        else:
            temp = f"{current.get('temp_C', 'N/A')}°C"
        
        return WeatherInfo(
            location=location_name,
            temperature=temp,
            description=current.get("weatherDesc", [{}])[0].get("value", "Unknown"),
            humidity=f"{current.get('humidity', 'N/A')}%",
            wind=f"{current.get('windspeedKmph', 'N/A')} km/h",
        )
    except Exception as e:
        return WeatherInfo(
            location=location,
            temperature="N/A",
            description=f"Error: {e}",
            humidity="N/A",
            wind="N/A",
        )


def get_forecast(
    location: str,
    days: int = 3,
    units: str = "metric",
) -> list[ForecastDay]:
    """
    Get multi-day forecast for a location.
    
    Args:
        location: City name
        days: Number of days (1-3)
        units: "metric" or "imperial"
    
    Returns:
        List of ForecastDay objects
    """
    url = f"https://wttr.in/{urllib.parse.quote(location)}?format=j1"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        
        forecasts = []
        for day_data in data.get("weather", [])[:days]:
            if units == "imperial":
                high = f"{day_data.get('maxtempF', 'N/A')}°F"
                low = f"{day_data.get('mintempF', 'N/A')}°F"
            else:
                high = f"{day_data.get('maxtempC', 'N/A')}°C"
                low = f"{day_data.get('mintempC', 'N/A')}°C"
            
            hourly = day_data.get("hourly", [{}])[0]
            desc = hourly.get("weatherDesc", [{}])[0].get("value", "Unknown")
            
            forecasts.append(ForecastDay(
                date=day_data.get("date", "Unknown"),
                temperature_high=high,
                temperature_low=low,
                description=desc,
            ))
        
        return forecasts
    except Exception as e:
        return [ForecastDay(
            date="Error",
            temperature_high="N/A",
            temperature_low="N/A",
            description=str(e),
        )]


def execute(params: dict) -> dict:
    """
    Execute weather skill.
    
    Args:
        params: Dict with 'location' (required) and 'action' (optional)
    
    Returns:
        Result dict
    """
    location = params.get("location")
    if not location:
        return {
            "success": False,
            "error": "Location is required",
        }
    
    action = params.get("action", "current")
    units = params.get("units", "metric")
    
    if action == "forecast":
        days = params.get("days", 3)
        forecast = get_forecast(location, days, units)
        return {
            "success": True,
            "location": location,
            "forecast": [
                {
                    "date": f.date,
                    "high": f.temperature_high,
                    "low": f.temperature_low,
                    "description": f.description,
                }
                for f in forecast
            ],
        }
    else:
        weather = get_weather(location, units)
        return {
            "success": True,
            "location": weather.location,
            "temperature": weather.temperature,
            "description": weather.description,
            "humidity": weather.humidity,
            "wind": weather.wind,
        }


if __name__ == "__main__":
    # Demo
    print("Current weather in Beijing:")
    print(get_weather("Beijing"))
    print()
    
    print("3-day forecast for Shanghai:")
    for day in get_forecast("Shanghai", days=3):
        print(f"  {day}")
