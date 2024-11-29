import requests
import openai
import json
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from googleapiclient.discovery import build

openweather_api_key = "your_api"
openai.api_key = "your_api"
google_search_api_key = "your_api"
CSE_ID = "your_api"

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
        "description": "can get current time and date of given city, can also be called if you just want the date",
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
    },
    {
        "name": "google_search",
        "description": "Perform a Google search and retrieve search results when user asks for.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string",
                },
                "num_results": {
                    "type": "integer",
                    "description": "The number of search results to return (max 10 per request).",
                    "default": 5,
                }
            },
            "required": ["query"],
        }
    },
    {
        "name": "search_arxiv",
        "description": "Search arXiv for academic papers based on a given query. Returns information about relevant papers, including title, authors, summary, publication date, and link.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string, e.g., 'quantum computing'.",
                },
                "num_results": {
                    "type": "integer",
                    "description": "The maximum number of results to return (default 5).",
                    "default": 5,
                }
            },
            "required": ["query"],
        }
    },
    {
        "name": "search_youtube",
        "description": "Search YouTube for videos based on a given query. Returns information about relevant videos, including title and link.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string, e.g., 'Python tutorial'.",
                },
                "num_results": {
                    "type": "integer",
                    "description": "The maximum number of video results to return (default 5).",
                    "default": 5,
                }
            },
            "required": ["query"],
        }
    }
]





def get_weather(city_name: str) -> str:
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={openweather_api_key}&units=metric&lang=en"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return data
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

def google_search(query, num_results=5):
    """
    Use Google Custom Search JSON API to perform searches.

    Parameters:
    - query: Search keyword (str)
    - num_results: Number of results to return, default is 10 (int)

    Returns:
    - List of search results, each containing title, link, and snippet.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    results = []

    try:
        params = {
            'q': query,
            'key': google_search_api_key,
            'cx': CSE_ID,
            'num': min(num_results, 10),  # Maximum 10 results per request
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        for item in data.get('items', []):
            result = {
                'title': item.get('title'),
                'link': item.get('link'),
                'snippet': item.get('snippet'),
            }
            results.append(result)

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except KeyError as e:
        print(f"Failed to parse response: {e}")

    return results

def search_arxiv(query, num_results=5):
    """
    Search arXiv for papers and return the results.

    Parameters:
    - query (str): Search keywords, supports boolean operators.
    - num_results (int): Maximum number of results to return, default is 5.

    Returns:
    - list of dict: A list of dictionaries containing paper information.
      Each dictionary includes title, authors, summary, published date, and link.
    """
    # Base API URL
    base_url = "http://export.arxiv.org/api/query"

    # Query parameters
    params = {
        "search_query": query,
        "start": 0,
        "max_results": num_results
    }

    # Send the request
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from arXiv. HTTP Status Code: {response.status_code}")

    # Parse the XML response
    root = ET.fromstring(response.text)
    results = []

    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        # Get the title
        title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
        # Get the authors
        authors = [
            author.find("{http://www.w3.org/2005/Atom}name").text.strip()
            for author in entry.findall("{http://www.w3.org/2005/Atom}author")
        ]
        # Get the summary
        summary = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip()
        # Get the published date
        published = entry.find("{http://www.w3.org/2005/Atom}published").text.strip()
        # Get the link
        link = entry.find("{http://www.w3.org/2005/Atom}id").text.strip()

        # Add to the results list
        results.append({
            "title": title,
            "authors": authors,
            "summary": summary,
            "published": published,
            "link": link
        })

    return results

def search_youtube(query, num_results=5):
    """
    Use YouTube Data API to search for videos.

    Parameters:
        query (str): Search keywords.
        num_results (int): Number of search results to return, default is 5.

    Returns:
        list: A list of dictionaries containing video titles and links.
    """
    API_KEY = google_search_api_key
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    # Build the API client
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

    # Call the search API
    search_response = youtube.search().list(
        q=query,  # Search keywords
        part='snippet',  # Returned resource part
        maxResults=num_results,  # Number of results
        type='video'  # Search type: video
    ).execute()

    # Parse search results
    results = []
    for item in search_response.get('items', []):
        video_id = item['id']['videoId']  # Video ID
        title = item['snippet']['title']  # Video title
        link = f'https://www.youtube.com/watch?v={video_id}'  # Video link
        results.append({'title': title, 'link': link})

    return results

# Define a function dispatcher
FUNCTIONS = {
    "get_weather": get_weather,
    "get_current_time": get_current_time,
    "google_search": google_search,
    "search_arxiv": search_arxiv,
    "search_youtube": search_youtube
}
if __name__ == "__main__":
    print(get_weather('london'))
