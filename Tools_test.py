import requests
import openai
import json
from datetime import datetime, timedelta

tools = [
    {
        "name": "get_weather",
        "description": "Get real-time weather information for a specified city. It also can get the coordinate of the city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": "cityname，eg：shanghai, new york or london. Has to be in english",
                }
            },
            "required": ["city_name"],
        },
    },
    {
        "name": "get_current_time",
        "description": "can get current time and date of given timezone, can also be called if you just want the date",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone_offset": {
                    "type": "integer",
                    "description": "timezone, for example given shanghai, you should get its timezone first, which is 8 here. If the city is not popular, you can use get_weather first to get its longitude",
                }
            },
            "required": ["timezone_offset"],
    }
    }
]



def get_weather(city_name: str) -> str:
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={openweather_api_key}&units=metric&lang=en"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return json.dumps(data)
        else:
            return f"❌ Unable to fetch weather information, error message: {data.get('message', 'Unknown error')}"
    except Exception as e:
        return f"❌ Error occurred while fetching weather information: {str(e)}"

def get_current_time(timezone_offset: int) -> str:
    try:
        # Get the current UTC time
        utc_now = datetime.utcnow()

        # Calculate the local time using the timezone offset
        local_time = utc_now + timedelta(hours=timezone_offset)

        # Format the local time as a string
        return local_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return f"error: Unable to get current time, message:{str(e)}"

# Define a function dispatcher
FUNCTIONS = {
    "get_weather": get_weather,
    "get_current_time": get_current_time
}

def handle_function_call(function_call):
    try:
        # Get function name and arguments
        function_name = function_call.name
        arguments = json.loads(function_call.arguments)  # Convert JSON string to dictionary

        # Call the corresponding function
        if function_name in FUNCTIONS:
            result = FUNCTIONS[function_name](**arguments)
            return result
        else:
            raise ValueError(f"Function '{function_name}' is not implemented.")
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    openweather_api_key = "your_api"
    openai.api_key = "your_api"

    messages = []
    messages.append(
        {
            "role": "system",
            "content": "your name is ZZZ_Bot."
        }
    )
    messages.append(
        {
            "role": "user",
            "content": "I'm in London now, what is the time?"
        }
    )

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        functions=tools,
        function_call="auto",  # Automatically decide whether to call a function
        max_tokens=1000,
    )

    # Append the returned message content
    messages.append(response.choices[0].message.model_dump())

    if response.choices[0].message.function_call is not None:
        function_call_info = response.choices[0].message.function_call
        arg = json.loads(response.choices[0].message.function_call.arguments)
        messages.append(
            {
                "role": "function",
                "name": function_call_info.name,
                "content": json.dumps(handle_function_call(function_call_info))
            }
        )

        print(messages)
        second_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,  # Adjust reply randomness
            max_tokens=1000,
        )
        print(second_response.choices[0].message.content)
