---
name: weather
version: 1.0.0
description: Weather query using wttr.in API with multi-city support
author: SkillHub
tags: weather, api, forecast
---

# Weather Skill

Get current weather and forecasts for any city using the wttr.in API.

## Features

- Current weather conditions
- Multi-day forecasts (up to 3 days)
- Multiple city queries in one request
- Automatic location detection
- Multiple output formats

## Usage

### Get Current Weather
```python
# Single city
weather = get_weather("Beijing")

# Multiple cities
weather = get_weather(["Beijing", "Shanghai", "Shenzhen"])
```

### Get Forecast
```python
# 3-day forecast
forecast = get_forecast("Beijing", days=3)
```

### Get Detailed Weather
```python
# Full weather report
report = get_detailed_weather("Beijing")
```

## Output Format

Returns weather information including:
- Temperature (current, feels like)
- Weather description
- Humidity
- Wind speed and direction
- Visibility
- UV index
- Precipitation probability

## Actions

- `get_weather`: Get current weather for one or more cities
- `get_forecast`: Get multi-day weather forecast
- `get_detailed_weather`: Get detailed weather report

## API

Uses the free wttr.in API: https://wttr.in
