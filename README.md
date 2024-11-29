Submission for Aipo Labs' Trial Project By Zihui Zhao

This submission includes a simple chatbot implemented as a Telegram bot. This chatbot uses the gpt-4o-mini language model to assist users with various tasks through a natural language interface.

Key Features
The bot is equipped with five primary functions that can be autonomously invoked by the LLM based on user input. These features include:

Real-Time Weather Information: Provides weather updates for specified cities.
Time and Date Queries: Offers the current time and date across different time zones.
Google Search: Performs online searches to retrieve information on diverse topics.
Academic Paper Search: Finds relevant academic papers from arXiv based on user queries.
YouTube Video Search: Searches YouTube for videos matching the user's description.

Code Structure
main.py: The central script that integrates the chatbot with Telegram and orchestrates interactions with the LLM.
Tools.py: Contains the implementation of the five core functions.
Testing Files:
Tool_test.py and telegram_test.py are provided for testing purposes only and are not required for deployment.
These two main files, main.py and Tools.py, are the most crucial for deployment.

Setup and Configuration
To set up the chatbot, the following API keys are required:

telegram_token: Connects the bot to the Telegram platform.
openai.api_key: Accesses the GPT-4o-mini language model.
openweather_api_key: Fetches weather information.
google_search_api_key: Enables Google and YouTube search functionalities.
CSE_ID: The Custom Search Engine ID for Google.
Simply replace the placeholder values in the code with the actual API keys to configure the bot.

Summary
This project implements a Telegram chatbot, ZZZ_Bot, designed to provide a range of functionalities using AI and external APIs.
