import requests
import streamlit as st
from datetime import datetime
import pytz
from tzwhere import tzwhere

# Set Streamlit page configuration
st.set_page_config(page_title="Weather App", layout="centered")
st.title("Weather App")

API_key = "37d1174f343a0198e1ef81d590f1c13a"
limit = 1

# Get user's local time
local_time = datetime.now()
local_time_str = local_time.strftime("%A, %d %B %Y %H:%M:%S")
st.sidebar.markdown("### Your Local Date & Time")
st.sidebar.success(local_time_str)

# City input field
city_name = st.text_input("Enter a city name:").capitalize()

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

            # Use tzwhere to get timezone name
            tz = tzwhere.tzwhere()
            tz_name = tz.tzNameAt(lat, lon)

            if tz_name is None:
                st.warning("Could not determine timezone for this location.")
            else:
                # Get accurate local time using timezone name
                location_time = datetime.now(pytz.timezone(tz_name))
                location_time_str = location_time.strftime("%A, %d %B %Y %H:%M:%S")

                # Get weather data
                respond1 = requests.get(
                    f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&units=metric"
                )
                respond1.raise_for_status()
                current_weather = respond1.json()

                weather = current_weather['weather'][0]
                main = current_weather['main']
                wind = current_weather['wind']
                sys = current_weather['sys']

                # Display weather icon
                icon_code = weather['icon']
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
                st.image(icon_url, caption=weather['description'].capitalize(), width=100)

                # Display location time
                st.markdown(f"### Local time in {city_name}, {sys['country']}")
                st.info(location_time_str)

                # Display weather metrics
                st.metric(label="Temperature", value=f"{round(main['temp'], 1)}°C")
                st.metric(label="Max Temperature", value=f"{round(main['temp_max'], 1)}°C")
                st.metric(label="Min Temperature", value=f"{round(main['temp_min'], 1)}°C")
                st.metric(label="Humidity", value=f"{main['humidity']}%")
                st.metric(label="Wind Speed", value=f"{wind['speed']} m/s")

                st.success("Have a great day!")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Please enter a valid city name.")