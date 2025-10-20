import logging
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.event import async_track_time_interval, async_track_state_change

_LOGGER = logging.getLogger(__name__)
DOMAIN = "hue_weather_adaptive"


# 🌞 Determine time slot dynamically
def get_time_slot() -> str:
    """Return morning, evening, or night based on current time."""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 19:
        return "evening"
    else:
        return "night"


# 🎨 Define lighting moods based on weather + time
def get_adaptive_scene(condition: str, time_slot: str):
    """Return (mode_name, hex_color, brightness, description)."""
    condition = condition.lower()

    scenes = {
        "clear": {
            "morning": ("Radiant Sunrise ☀️", "#FFD580", 255, "Bright golden hue to energize your morning."),
            "evening": ("Golden Sunset 🌇", "#FFB347", 200, "Warm orange tones for a relaxing sunset."),
            "night": ("Calm Moonlight 🌙", "#F5F3CE", 120, "Soft white calm for clear night skies."),
        },
        "cloud": {
            "morning": ("Misty Morning ☁️", "#C0D6DF", 220, "Cool white tones for a foggy start."),
            "evening": ("Dusky Grey 🌫️", "#A9A9A9", 180, "Balanced neutral tones for cloudy evenings."),
            "night": ("Overcast Night 🌌", "#B0C4DE", 100, "Dim bluish-gray to reflect a moody sky."),
        },
        "rain": {
            "morning": ("Rainy Dawn 🌧️", "#9CC4B2", 180, "Soft teal mood for a gentle rainy morning."),
            "evening": ("Cozy Rainlight ☕", "#FFB6A1", 160, "Warm amber glow for rainy evenings."),
            "night": ("Rainy Calm 🌧️🌙", "#8AA7A9", 80, "Cool, low-intensity lighting for quiet rain nights."),
        },
        "snow": {
            "morning": ("Frosty Morning ❄️", "#E8F9FD", 230, "Pure white brightness reflecting snow glow."),
            "evening": ("Chilly Twilight 🧊", "#CFE9F3", 180, "Cool blue calm for snowy evenings."),
            "night": ("Winter Night ❄️🌙", "#A8D0E6", 90, "Subtle icy hue for frozen nights."),
        },
        "fog": {
            "morning": ("Foggy Dawn 🌫️", "#D3D3D3", 180, "Soft diffused light for misty mornings."),
            "evening": ("Low Mist Glow 🌁", "#C0C0C0", 150, "Muted greyish white for foggy dusk."),
            "night": ("Dense Foglight 🌫️🌙", "#BEBEBE", 80, "Dim silver haze for thick fog nights."),
        },
    }

    default_scene = ("Soft Neutral Light 🌗", "#FFF8DC", 180, "Balanced tone for undefined conditions.")

    for key, moods in scenes.items():
        if key in condition:
            return moods.get(time_slot, default_scene)
    return default_scene


async def async_setup(hass: HomeAssistant, config: dict):
    """Initialize the adaptive lighting integration with real-time updates."""
    _LOGGER.info("🌈 Initializing Hue Weather Adaptive AI (Real-Time Mode)...")

    # Change these to your actual entities
    weather_entity = "weather.home"
    light_entity = "light.hue_test_light"
# HEX → RGB helper
    def _hex_to_rgb(hex_color: str):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # 💡 Main logic — updates lighting based on weather + time
    async def update_lighting(reason: str = "Manual Trigger"):
        weather = hass.states.get(weather_entity)
        if not weather:
            _LOGGER.error(f"Weather entity '{weather_entity}' not found.")
            return

        condition = weather.state.lower().strip()
        time_slot = get_time_slot()
        mode_name, color_hex, brightness, desc = get_adaptive_scene(condition, time_slot)

        _LOGGER.info(f"[{reason}] 🌤 {condition} | {time_slot} | Mode: {mode_name} | {color_hex}")

        await hass.services.async_call(
            "light",
            "turn_on",
            {
                "entity_id": light_entity,
                "brightness": brightness,
                "rgb_color": _hex_to_rgb(color_hex),
                "transition": 8,
            },
        )

        hass.components.persistent_notification.create(
            f"<b>{reason}</b><br>"
            f"<b>Condition:</b> {condition.capitalize()}<br>"
            f"<b>Time:</b> {time_slot.capitalize()}<br>"
            f"<b>Mode:</b> {mode_name}<br>"
            f"<b>Color:</b> {color_hex}<br>"
            f"<b>Description:</b> {desc}",
            title="💡 Hue Weather AI Adaptive Update",
        )

    # 🧠 Trigger updates when weather changes
    @callback
    async def weather_changed(entity, old_state, new_state):
        if not new_state or not old_state:
            return
        if new_state.state != old_state.state:
            _LOGGER.info(f"🌦 Weather changed from '{old_state.state}' → '{new_state.state}'")
            await update_lighting(reason="Weather Change Detected")

    async_track_state_change(hass, weather_entity, weather_changed)

    # 🕒 Still runs every 30 mins as backup (in case API misses an event)
    async_track_time_interval(
        hass, lambda _: hass.async_create_task(update_lighting(reason="Scheduled Refresh")), timedelta(minutes=30)
    )

    # Manual trigger (optional)
    async def manual_apply(call: ServiceCall):
        await update_lighting(reason="Manual Service Call")

    hass.services.async_register(DOMAIN, "apply_weather_mode", manual_apply)

    # Run once at startup
    hass.async_create_task(update_lighting(reason="Startup Initialization"))

    _LOGGER.info("✅ Hue Weather Adaptive AI (Real-Time) is active.")
    return True