import requests
from langchain_core.tools import Tool


def get_weather(city: str) -> str:

    try:

        api_key = "a9f3e3a73446aa1c150ba56ac93e22dc"

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={api_key}&units=metric"
        )

        response = requests.get(url, timeout=10)

        data = response.json()

        if data.get("cod") != 200:
            return f"City not found: {city}"

        weather = data["weather"][0]["description"]
        temp    = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        return (
            f"Weather in {city}\n"
            f"Condition: {weather}\n"
            f"Temperature: {temp}°C\n"
            f"Humidity: {humidity}%"
        )

    except Exception as e:

        return f"Weather Error: {str(e)}"


weather_tool = Tool(
    name="Weather",
    func=get_weather,
    description="Get current weather for a city"
)