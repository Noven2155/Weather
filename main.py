

import requests
import streamlit as st
from datetime import datetime
import pytz

#  Add modules for JSON and file handling
import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {
        "default_location": "Tel Aviv",
        "unit": "metric",  # or 'imperial'
        "favorites": []
    }

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

settings = load_settings()


# Set Streamlit page configuration
st.set_page_config(page_title="Weather App", layout="centered")
st.title("Weather App")

API_key = "37d1174f343a0198e1ef81d590f1c13a"
limit = 1

# Get user's local time
tz = pytz.timezone("Asia/Jerusalem")
local_time = datetime.now(tz)
local_time_str = local_time.strftime("%A, %d %B %Y %H:%M:%S")

# Display local time in sidebar
st.sidebar.markdown("### Your Local Date & Time")
st.sidebar.success(local_time_str)

# Preferences menu
st.sidebar.markdown("### Preferences")

# Set default city and temperature unit
default_city = st.sidebar.text_input("Set default city:", value=settings["default_location"])
unit = st.sidebar.selectbox("Select temperature unit:", ["metric", "imperial"],
                            index=["metric", "imperial"].index(settings["unit"]))

# Add favorite city
new_favorite = st.sidebar.text_input("Add favorite city:")
if st.sidebar.button("Add City"):
    if new_favorite:
        settings["favorites"].append(new_favorite.capitalize())
        st.sidebar.success(f"{new_favorite.capitalize()} added to favorites.")
        save_settings(settings)

# Remove favorite city
remove_city = st.sidebar.selectbox("Remove favorite city:", options=[""] + settings["favorites"])
if st.sidebar.button("Remove City"):
    if remove_city and remove_city in settings["favorites"]:
        settings["favorites"].remove(remove_city)
        st.sidebar.success(f"{remove_city} removed from favorites.")
        save_settings(settings)

# Save default city and unit automatically
settings["default_location"] = default_city.capitalize()
settings["unit"] = unit
save_settings(settings)

# Show current favorites and allow selection
if settings["favorites"]:
    st.sidebar.markdown("### Favorite Cities:")

    # Dropdown menu to select a city from favorites
    selected_favorite = st.sidebar.selectbox("Choose from favorites:", options=[""] + settings["favorites"])

    # If user selects a favorite and doesn't enter a new city, use the favorite
    if selected_favorite and not city_name:
        city_name = selected_favorite



# Use default city if no input is provided
city_name = st.text_input("Enter a city name:").capitalize()
if not city_name:
    city_name = settings.get("default_location", "Tel Aviv").capitalize()


if city_name:
    try:
        # Get location details (latitude and longitude)
        respond = requests.get(
            f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit={limit}&appid={API_key}"
        )
        respond.raise_for_status()
        data = respond.json()

        if not data:
            st.warning("City not found. Please try again.")
        else:
            lat = data[0]['lat']
            lon = data[0]['lon']

            # Apply user's temperature unit
            units = settings.get("unit", "metric")
            temp_symbol = "°C" if units == "metric" else "°F"


            # Get weather data using coordinates
            respond1 = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&units={units}"
            )
            respond1.raise_for_status()
            current_weather = respond1.json()

            weather = current_weather['weather'][0]
            main = current_weather['main']
            wind = current_weather['wind']
            sys = current_weather['sys']
            timezone_offset = current_weather['timezone']  # in seconds

            # Convert timezone offset to datetime
            location_timezone = pytz.FixedOffset(timezone_offset // 60)
            location_time = datetime.now(location_timezone)
            location_time_str = location_time.strftime("%A, %d %B %Y %H:%M:%S")

            # Weather icon from OpenWeatherMap
            icon_code = weather['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            st.image(icon_url, caption=weather['description'].capitalize(), width=100)

            # Display local time in the selected location
            st.markdown(f"### Local time in {city_name}, {sys['country']}")
            st.info(location_time_str)

            # Display weather data as metrics
            st.metric(label="Temperature", value=f"{round(main['temp'], 1)}{temp_symbol}")
            st.metric(label="Max Temperature", value=f"{round(main['temp_max'], 1)}{temp_symbol}")
            st.metric(label="Min Temperature", value=f"{round(main['temp_min'], 1)}{temp_symbol}")
            st.metric(label="Humidity", value=f"{main['humidity']}%")
            st.metric(label="Wind Speed", value=f"{wind['speed']} m/s")

            # Final message
            st.success("Have a great day!")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Please enter a valid city name.")