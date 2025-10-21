import pytest
from datetime import datetime

# -------------------------------------------------------------
# 💡 Standalone replica of your hue_weather_adaptive logic
# -------------------------------------------------------------
def get_light_mode(weather: str, current_time: datetime) -> str:
    """Simplified version of your adaptive lighting logic."""
    hour = current_time.hour

    if weather.lower() in ("rain", "storm", "snow"):
        return "Soft Amber 🌙🌧️" if hour >= 18 or hour < 6 else "Neutral Daylight 🌦️"
    elif weather.lower() in ("sunny", "clear"):
        return "Bright Daylight ☀️" if 7 <= hour <= 17 else "Cool Dimmed 💡"
    elif weather.lower() in ("cloudy", "overcast"):
        return "Cool Dimmed ☁️" if 17 <= hour <= 19 else "Neutral Daylight 🌤️"
    else:
        return "Neutral Light 🌗"


# -------------------------------------------------------------
# ✅ TEST CASES
# -------------------------------------------------------------
def test_bright_daylight_mode():
    """☀️ Sunny daytime should trigger Bright Daylight."""
    mode = get_light_mode("sunny", datetime(2025, 10, 21, 10, 0, 0))
    assert mode == "Bright Daylight ☀️"
    print("✅ Passed: Bright Daylight ☀️ mode correct")


def test_soft_amber_mode():
    """🌙 Rainy nighttime should trigger Soft Amber."""
    mode = get_light_mode("rain", datetime(2025, 10, 21, 22, 0, 0))
    assert mode == "Soft Amber 🌙🌧️"
    print("✅ Passed: Soft Amber 🌙🌧️ mode correct")


def test_cloudy_transition_mode():
    """☁️ Cloudy evening should trigger Cool Dimmed."""
    mode = get_light_mode("cloudy", datetime(2025, 10, 21, 18, 0, 0))
    assert "Cool Dimmed" in mode
    print("✅ Passed: Cloudy Cool Dimmed ☁️ mode correct")
