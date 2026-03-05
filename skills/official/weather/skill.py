#!/usr/bin/env python3
"""
Weather Skill - Weather queries using wttr.in API
"""

import urllib.request
import urllib.error
import json
from typing import Dict, Any, List, Union, Optional


class WeatherSkill:
    """Weather query using wttr.in API"""
    
    def __init__(self):
        self.base_url = "https://wttr.in"
        self.timeout = 10
    
    def get_weather(self, locations: Union[str, List[str]], format: str = 'j1') -> Dict[str, Any]:
        """
        Get current weather for one or more locations
        
        Args:
            locations: City name or list of city names
            format: Response format (j1 for JSON, v2 for detailed)
            
        Returns:
            Dictionary with weather data
        """
        if isinstance(locations, str):
            locations = [locations]
        
        results = {}
        
        for location in locations:
            try:
                weather_data = self._fetch_weather(location, format)
                if weather_data:
                    results[location] = self._parse_current_weather(weather_data)
                else:
                    results[location] = {'error': 'Failed to fetch weather data'}
            except Exception as e:
                results[location] = {'error': str(e)}
        
        return {
            'success': all('error' not in v for v in results.values()),
            'weather': results,
            'count': len(results)
        }
    
    def get_forecast(self, location: str, days: int = 3) -> Dict[str, Any]:
        """
        Get multi-day weather forecast
        
        Args:
            location: City name
            days: Number of days (1-3)
            
        Returns:
            Dictionary with forecast data
        """
        try:
            weather_data = self._fetch_weather(location, 'j1')
            if not weather_data:
                return {
                    'success': False,
                    'error': 'Failed to fetch weather data'
                }
            
            # Parse forecast
            forecasts = []
            weather_list = weather_data.get('weather', [])
            
            for i, day_data in enumerate(weather_list[:days]):
                forecast = {
                    'date': day_data.get('date'),
                    'max_temp': day_data.get('maxtempC'),
                    'min_temp': day_data.get('mintempC'),
                    'avg_temp': day_data.get('avgtempC'),
                    'total_snow': day_data.get('totalSnow_cm'),
                    'sun_hour': day_data.get('sunHour'),
                    'uv_index': day_data.get('uvIndex'),
                    'hourly': self._parse_hourly(day_data.get('hourly', []))
                }
                forecasts.append(forecast)
            
            return {
                'success': True,
                'location': location,
                'forecast': forecasts,
                'days': len(forecasts)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_detailed_weather(self, location: str) -> Dict[str, Any]:
        """
        Get detailed weather report
        
        Args:
            location: City name
            
        Returns:
            Dictionary with detailed weather information
        """
        try:
            weather_data = self._fetch_weather(location, 'j1')
            if not weather_data:
                return {
                    'success': False,
                    'error': 'Failed to fetch weather data'
                }
            
            current = weather_data.get('current_condition', [{}])[0]
            
            return {
                'success': True,
                'location': location,
                'area': weather_data.get('nearest_area', [{}])[0],
                'current': {
                    'temp_c': current.get('temp_C'),
                    'temp_f': current.get('temp_F'),
                    'feels_like_c': current.get('FeelsLikeC'),
                    'feels_like_f': current.get('FeelsLikeF'),
                    'description': current.get('weatherDesc', [{}])[0].get('value'),
                    'humidity': current.get('humidity'),
                    'wind_speed_kph': current.get('windspeedKmph'),
                    'wind_dir': current.get('winddir16Point'),
                    'pressure': current.get('pressure'),
                    'visibility': current.get('visibility'),
                    'uv_index': current.get('uvIndex'),
                    'cloud_cover': current.get('cloudcover'),
                    'precip_mm': current.get('precipMM'),
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _fetch_weather(self, location: str, format: str = 'j1') -> Optional[Dict]:
        """Fetch weather data from wttr.in"""
        try:
            url = f"{self.base_url}/{location}?format={format}"
            
            # Create request with headers
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'curl/7.68.0')  # wttr.in prefers curl-like UA
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = response.read().decode('utf-8')
                
                if format == 'j1':
                    return json.loads(data)
                else:
                    return {'raw': data}
        except urllib.error.URLError as e:
            print(f"URL Error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON Error: {e}")
            return None
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None
    
    def _parse_current_weather(self, data: Dict) -> Dict:
        """Parse current weather from API response"""
        try:
            current = data.get('current_condition', [{}])[0]
            area = data.get('nearest_area', [{}])[0]
            
            return {
                'location': area.get('areaName', [{}])[0].get('value', 'Unknown'),
                'country': area.get('country', [{}])[0].get('value', 'Unknown'),
                'temp_c': current.get('temp_C'),
                'temp_f': current.get('temp_F'),
                'description': current.get('weatherDesc', [{}])[0].get('value'),
                'humidity': current.get('humidity'),
                'wind_speed_kph': current.get('windspeedKmph'),
                'wind_dir': current.get('winddir16Point'),
            }
        except Exception:
            return {'error': 'Failed to parse weather data'}
    
    def _parse_hourly(self, hourly_data: List) -> List[Dict]:
        """Parse hourly forecast data"""
        hourly = []
        for hour in hourly_data:
            hourly.append({
                'time': hour.get('time'),
                'temp_c': hour.get('tempC'),
                'description': hour.get('weatherDesc', [{}])[0].get('value'),
                'precip_mm': hour.get('precipMM'),
                'humidity': hour.get('humidity'),
            })
        return hourly


# Skill interface
_skill_instance = None

def get_skill():
    """Get or create skill instance"""
    global _skill_instance
    if _skill_instance is None:
        _skill_instance = WeatherSkill()
    return _skill_instance


def execute(action: str, **kwargs) -> Dict[str, Any]:
    """
    Execute skill action
    
    Args:
        action: Action to perform (get_weather, get_forecast, get_detailed_weather)
        **kwargs: Action-specific parameters
        
    Returns:
        Result dictionary
    """
    skill = get_skill()
    
    if action == 'get_weather':
        locations = kwargs.get('locations')
        if not locations:
            return {'success': False, 'error': 'Missing locations parameter'}
        return skill.get_weather(locations)
    
    elif action == 'get_forecast':
        location = kwargs.get('location')
        days = kwargs.get('days', 3)
        if not location:
            return {'success': False, 'error': 'Missing location parameter'}
        return skill.get_forecast(location, days)
    
    elif action == 'get_detailed_weather':
        location = kwargs.get('location')
        if not location:
            return {'success': False, 'error': 'Missing location parameter'}
        return skill.get_detailed_weather(location)
    
    else:
        return {
            'success': False,
            'error': f'Unknown action: {action}. Available actions: get_weather, get_forecast, get_detailed_weather'
        }


if __name__ == '__main__':
    # Test the skill
    print("Testing Weather Skill...")
    
    # Test current weather
    result = execute('get_weather', locations='Beijing')
    print(f"\nCurrent weather in Beijing:\n{json.dumps(result, indent=2)}")
    
    # Test multiple cities
    result = execute('get_weather', locations=['Beijing', 'Shanghai'])
    print(f"\nWeather for multiple cities:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
