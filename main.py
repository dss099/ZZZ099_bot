import os
import openai
import requests
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import Tools
from Tools import FUNCTIONS, tools


telegram_token = "your_api"

messages = []
messages.append(
    {
        "role": "system",
        "content": "your name is ZZZ_Bot, you are a chat bot. Your creator is Zihui Zhao"
                   "you can use the 'get_weather' function when the user asks about the weather of a city. "
                   "If you are not sure, then do not make things up. You also use get_current_time to get the time and date info."
                   "You can use 'google_search' to search in google and get the info you need. If it is about the info of academic paper, you can use search_arxiv"
                   "You can use 'search_youtube' to search video on youtube"
    }
)

def chat_with_openai(prompt: str) -> str:
    messages.append({"role": "user", "content": prompt})  # Add user message to conversation history
    while True:  # handling multiple function calls
        try:
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # Or another available model
                messages=messages,
                functions=tools,
                function_call="auto",  # Automatically decide whether to call a function
                temperature=0.7,
                max_tokens=1000,
            )
            if response.choices[0].message.function_call != None:
                function_call_info = response.choices[0].message.function_call
                arg = json.loads(response.choices[0].message.function_call.arguments)
                messages.append(
                    {
                        "role": "function",
                        "name": function_call_info.name,
                        "content": json.dumps(handle_function_call(function_call_info))
                    }
                )

            else:
                reply = response.choices[0].message.content
                messages.append({"role": "assistant", "content": reply})  # Add assistant's reply to conversation history
                return reply
        except Exception as e:
            return f"An error occurred: {str(e)}"

def handle_function_call(function_call):
    try:
        # Get function name and arguments
        function_name = function_call.name
        arguments = json.loads(function_call.arguments)  # Convert JSON string to dictionary

        # Call the corresponding function
        if function_name in FUNCTIONS:
            #result = FUNCTIONS[function_name](**arguments)
            result = getattr(Tools, function_name, None)(**arguments)
            return result
        else:
            raise ValueError(f"Function '{function_name}' is not implemented.")
    except Exception as e:
        return {"error": str(e)}


# Define a function to handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text  # User's message
    response = chat_with_openai(user_message)  # Call OpenAI API to get a response
    await update.message.reply_text(response)  # Send the response back to the user


def main():
    # Adding command and message handlers
    app = ApplicationBuilder().token(telegram_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
    #print(getattr(Tools, 'get_weather', None)('london'))
