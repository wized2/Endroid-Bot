import discord

from discord import app_commands

from discord.ext import commands

import aiohttp

import asyncio

import config

from datetime import datetime

class Weather(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.geocoding_api = "https://geocoding-api.open-meteo.com/v1/search"

        self.weather_api = "https://api.open-meteo.com/v1/forecast"

    

    # WMO Weather interpretation codes (WW)

    def get_weather_description(self, code: int) -> tuple:

        """Returns (description, emoji) for WMO weather code"""

        weather_codes = {

            0: ("Clear sky", "☀️"),

            1: ("Mainly clear", "🌤️"),

            2: ("Partly cloudy", "⛅"),

            3: ("Overcast", "☁️"),

            45: ("Fog", "🌫️"),

            48: ("Depositing rime fog", "🌫️"),

            51: ("Light drizzle", "🌦️"),

            53: ("Moderate drizzle", "🌦️"),

            55: ("Dense drizzle", "🌧️"),

            56: ("Light freezing drizzle", "🌨️"),

            57: ("Dense freezing drizzle", "🌨️"),

            61: ("Slight rain", "🌦️"),

            63: ("Moderate rain", "🌧️"),

            65: ("Heavy rain", "🌧️💧"),

            66: ("Light freezing rain", "🌨️"),

            67: ("Heavy freezing rain", "🌨️❄️"),

            71: ("Slight snowfall", "🌨️"),

            73: ("Moderate snowfall", "❄️"),

            75: ("Heavy snowfall", "❄️❄️"),

            77: ("Snow grains", "❄️"),

            80: ("Slight rain showers", "🌦️"),

            81: ("Moderate rain showers", "🌧️"),

            82: ("Violent rain showers", "🌧️💦"),

            85: ("Slight snow showers", "🌨️"),

            86: ("Heavy snow showers", "❄️💨"),

            95: ("Thunderstorm", "⛈️"),

            96: ("Thunderstorm with slight hail", "⛈️🧊"),

            99: ("Thunderstorm with heavy hail", "⛈️💥")

        }

        return weather_codes.get(code, ("Unknown", "❓"))

    

    @app_commands.command(name="weather", description="Get current weather for any city worldwide!")

    @app_commands.describe(

        city="City name (e.g., London, Tokyo, New York)",

        units="Temperature units (Celsius or Fahrenheit)"

    )

    @app_commands.choices(units=[

        app_commands.Choice(name="Celsius (°C)", value="celsius"),

        app_commands.Choice(name="Fahrenheit (°F)", value="fahrenheit"),

    ])

    @app_commands.checks.cooldown(1, 10)  # 10 second cooldown

    async def weather(self, interaction: discord.Interaction, city: str, units: str = "celsius"):

        """Fetch and display current weather for a city"""

        

        # Defer response while we fetch data

        await interaction.response.defer()

        

        async with aiohttp.ClientSession() as session:

            try:

                # STEP 1: Geocode city name to coordinates

                geo_params = {

                    "name": city,

                    "count": 1,

                    "language": "en",

                    "format": "json"

                }

                

                async with session.get(self.geocoding_api, params=geo_params) as geo_response:

                    if geo_response.status != 200:

                        await interaction.followup.send(

                            f"{config.Icons.NO} Geocoding service error. Please try again.",

                            ephemeral=True

                        )

                        return

                    

                    geo_data = await geo_response.json()

                    

                    if not geo_data.get("results"):

                        await interaction.followup.send(

                            f"{config.Icons.NO} City '{city}' not found. Please check the spelling and try again.",

                            ephemeral=True

                        )

                        return

                    

                    # Get the first (best) match

                    location = geo_data["results"][0]

                    city_name = location.get("name", city)

                    country = location.get("country", "Unknown")

                    state = location.get("admin1", "")

                    latitude = location["latitude"]

                    longitude = location["longitude"]

                    elevation = location.get("elevation", 0)

                    population = location.get("population", "Unknown")

                    

                    # Format location display

                    location_display = city_name

                    if state:

                        location_display += f", {state}"

                    location_display += f", {country}"

                

                # STEP 2: Fetch current weather data

                weather_params = {

                    "latitude": latitude,

                    "longitude": longitude,

                    "current_weather": "true",

                    "timezone": "auto",

                    "hourly": "relative_humidity_2m,apparent_temperature,pressure_msl,visibility,cloudcover",

                    "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset",

                    "forecast_days": 1

                }

                

                # Add unit parameters

                if units == "fahrenheit":

                    weather_params["temperature_unit"] = "fahrenheit"

                    weather_params["windspeed_unit"] = "mph"

                    temp_unit = "°F"

                    wind_unit = "mph"

                else:

                    weather_params["temperature_unit"] = "celsius"

                    weather_params["windspeed_unit"] = "kmh"

                    temp_unit = "°C"

                    wind_unit = "km/h"

                

                async with session.get(self.weather_api, params=weather_params) as weather_response:

                    if weather_response.status != 200:

                        await interaction.followup.send(

                            f"{config.Icons.NO} Weather service error. Please try again.",

                            ephemeral=True

                        )

                        return

                    

                    weather_data = await weather_response.json()

                    

                    # Extract current weather

                    current = weather_data.get("current_weather", {})

                    temperature = current.get("temperature", "N/A")

                    windspeed = current.get("windspeed", "N/A")

                    winddirection = current.get("winddirection", "N/A")

                    weathercode = current.get("weathercode", 0)

                    is_day = current.get("is_day", 1)

                    update_time = current.get("time", datetime.utcnow().isoformat())

                    

                    # Get weather description and emoji

                    weather_desc, weather_emoji = self.get_weather_description(weathercode)

                    

                    # Extract hourly data

                    hourly = weather_data.get("hourly", {})

                    humidity = hourly.get("relative_humidity_2m", [0])[0] if hourly.get("relative_humidity_2m") else "N/A"

                    feels_like = hourly.get("apparent_temperature", [temperature])[0] if hourly.get("apparent_temperature") else temperature

                    pressure = hourly.get("pressure_msl", [0])[0] if hourly.get("pressure_msl") else "N/A"

                    visibility = hourly.get("visibility", [0])[0] if hourly.get("visibility") else "N/A"

                    cloudcover = hourly.get("cloudcover", [0])[0] if hourly.get("cloudcover") else "N/A"

                    

                    # Extract daily data

                    daily = weather_data.get("daily", {})

                    temp_max = daily.get("temperature_2m_max", [0])[0] if daily.get("temperature_2m_max") else "N/A"

                    temp_min = daily.get("temperature_2m_min", [0])[0] if daily.get("temperature_2m_min") else "N/A"

                    sunrise = daily.get("sunrise", [""])[0] if daily.get("sunrise") else "N/A"

                    sunset = daily.get("sunset", [""])[0] if daily.get("sunset") else "N/A"

                    

                    # Format times

                    try:

                        if sunrise != "N/A":

                            sunrise_time = datetime.fromisoformat(sunrise.replace("Z", "+00:00")).strftime("%H:%M")

                        else:

                            sunrise_time = "N/A"

                        if sunset != "N/A":

                            sunset_time = datetime.fromisoformat(sunset.replace("Z", "+00:00")).strftime("%H:%M")

                        else:

                            sunset_time = "N/A"

                        update_time_formatted = datetime.fromisoformat(update_time.replace("Z", "+00:00")).strftime("%H:%M")

                    except:

                        sunrise_time = sunrise

                        sunset_time = sunset

                        update_time_formatted = update_time

                    

                    # Create wind direction arrow

                    wind_arrows = ["↓", "↙", "←", "↖", "↑", "↗", "→", "↘"]

                    if isinstance(winddirection, (int, float)):

                        wind_index = round(winddirection / 45) % 8

                        wind_arrow = wind_arrows[wind_index]

                    else:

                        wind_arrow = "→"

                    

                    # Convert visibility to km

                    if isinstance(visibility, (int, float)):

                        visibility_km = visibility / 1000

                        visibility_display = f"{visibility_km:.1f} km"

                    else:

                        visibility_display = "N/A"

                    

                    # Convert pressure to hPa (already in hPa)

                    pressure_display = f"{pressure} hPa" if pressure != "N/A" else "N/A"

                    

                    # Format population with commas

                    if population != "Unknown" and isinstance(population, int):

                        population_display = f"{population:,}"

                    else:

                        population_display = "Unknown"

                    

                    # --- CREATE BEAUTIFUL EMBED ---

                    embed = discord.Embed(

                        title=f"{weather_emoji} Current Weather in {location_display}",

                        color=config.Colors.INFO,

                        url=f"https://open-meteo.com/?lat={latitude}&lon={longitude}&timezone=auto"

                    )

                    

                    # Main temperature field

                    embed.add_field(

                        name="🌡️ Temperature",

                        value=f"**{temperature}{temp_unit}**\nFeels like: {feels_like}{temp_unit}",

                        inline=True

                    )

                    

                    # Weather condition

                    embed.add_field(

                        name="☁️ Condition",

                        value=f"**{weather_desc}**\nCloud cover: {cloudcover}%",

                        inline=True

                    )

                    

                    # Humidity

                    embed.add_field(

                        name="💧 Humidity",

                        value=f"**{humidity}%**",

                        inline=True

                    )

                    

                    # Wind

                    embed.add_field(

                        name="💨 Wind",

                        value=f"**{windspeed} {wind_unit}**\nDirection: {winddirection}° {wind_arrow}",

                        inline=True

                    )

                    

                    # Pressure & Visibility

                    embed.add_field(

                        name="📊 Pressure",

                        value=f"**{pressure_display}**",

                        inline=True

                    )

                    

                    embed.add_field(

                        name="👁️ Visibility",

                        value=f"**{visibility_display}**",

                        inline=True

                    )

                    

                    # Daily min/max

                    embed.add_field(

                        name="📈 Daily Range",

                        value=f"Max: **{temp_max}{temp_unit}**\nMin: **{temp_min}{temp_unit}**",

                        inline=True

                    )

                    

                    # Sunrise/Sunset

                    embed.add_field(

                        name="🌅 Sunrise",

                        value=f"**{sunrise_time}**",

                        inline=True

                    )

                    

                    embed.add_field(

                        name="🌇 Sunset",

                        value=f"**{sunset_time}**",

                        inline=True

                    )

                    

                    # Location info

                    location_info = f"📍 Coordinates: `{latitude:.4f}, {longitude:.4f}`\n"

                    location_info += f"🏔️ Elevation: `{elevation}m`\n"

                    if population_display != "Unknown":

                        location_info += f"👥 Population: `{population_display}`"

                    

                    embed.add_field(

                        name="🗺️ Location Details",

                        value=location_info,

                        inline=False

                    )

                    

                    # Footer with update time

                    day_icon = "☀️ Day" if is_day == 1 else "🌙 Night"

                    embed.set_footer(

                        text=f"{day_icon} • Updated at {update_time_formatted} (Local Time) • Data: Open-Meteo",

                        icon_url="https://open-meteo.com/images/favicon.ico"

                    )

                    embed.timestamp = datetime.utcnow()

                    

                    # Set thumbnail based on weather

                    if is_day == 1:

                        if weathercode == 0:

                            embed.set_thumbnail(url="https://openweathermap.org/img/wn/01d@2x.png")

                        elif weathercode in [1, 2]:

                            embed.set_thumbnail(url="https://openweathermap.org/img/wn/02d@2x.png")

                        elif weathercode == 3:

                            embed.set_thumbnail(url="https://openweathermap.org/img/wn/03d@2x.png")

                        elif weathercode in [45, 48]:

                            embed.set_thumbnail(url="https://openweathermap.org/img/wn/50d@2x.png")

                        elif weathercode in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:

                            embed.set_thumbnail(url="https://openweathermap.org/img/wn/10d@2x.png")

                        elif weathercode in [71, 73, 75, 77, 85, 86]:

                            embed.set_thumbnail(url="https://openweathermap.org/img/wn/13d@2x.png")

                        elif weathercode in [95, 96, 99]:

                            embed.set_thumbnail(url="https://openweathermap.org/img/wn/11d@2x.png")

                    else:

                        if weathercode == 0:

                            embed.set_thumbnail(url="https://openweathermap.org/img/wn/01n@2x.png")

                        elif weathercode in [1, 2]:

                            embed.set_thumbnail(url="https://openweathermap.org/img/wn/02n@2x.png")

                        else:

                            embed.set_thumbnail(url="https://openweathermap.org/img/wn/04n@2x.png")

                    

                    await interaction.followup.send(embed=embed)

                    

            except aiohttp.ClientError:

                await interaction.followup.send(

                    f"{config.Icons.NO} Network error. Couldn't reach the weather service.",

                    ephemeral=True

                )

            except Exception as e:

                if config.BotConfig.LOG_ERRORS:

                    print(f"{config.Icons.NO} Weather command error: {e}")

                await interaction.followup.send(

                    f"{config.Icons.NO} An error occurred while fetching weather data.",

                    ephemeral=True

                )

async def setup(bot):

    await bot.add_cog(Weather(bot))