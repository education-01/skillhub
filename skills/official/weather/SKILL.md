---
name: weather
version: 1.0.0
description: Get weather information for any location
author: SkillHub Team
tags:
  - weather
  - api
dependencies:
  - requests>=2.28
license: MIT
homepage: https://github.com/skillhub/weather
---

# Weather Skill

Get current weather and forecasts for any location.

## Usage

```python
from weather import get_weather, get_forecast

# Get current weather
current = get_weather("Beijing")
print(current)

# Get forecast
forecast = get_forecast("Shanghai", days=3)
print(forecast)
```

## Features

- Current weather by city name
- Multi-day forecasts
- Supports multiple weather APIs
