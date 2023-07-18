# Importing required modules
import requests
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()  # Enanle environment variables from .env

# Setting constant variables
STOCK_NAME = os.getenv("STOCK_NAME")
COMPANY_NAME = os.getenv("COMPANY_NAME")
STOCK_API_KEY = os.getenv("STOCK_API_KEY")
STOCK_ENDPOINT = os.getenv("STOCK_ENDPOINT")  # https://www.alphavantage.co
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_ENDPOINT = os.getenv("NEWS_ENDPOINT")  # https://newsapi.org/
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Define parameters for the stock API request
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}

# Make a GET request to the stock API
response = requests.get(STOCK_ENDPOINT, params=stock_params)

# Parse the response JSON
data = response.json()["Time Series (Daily)"]

# Get the data for the two most recent days
data_list = [value for (key, value) in data.items()]
previous_day_data = data_list[0]
previous_closing_price = previous_day_data["4. close"]
day_before_previous_day_data = data_list[1]
day_before_yesterday_closing_price = day_before_previous_day_data["4. close"]

# Calculate the difference between the two days' closing prices
difference = abs(
    float(previous_closing_price) - float(day_before_yesterday_closing_price)
)

# Determine whether the price went up or down
up_down = None
if difference > 0:
    up_down = "📈"
else:
    up_down = "📉"

# Calculate the percent difference
diff_percent = round((difference / float(previous_closing_price)) * 100, 2)

# If the percent difference is more than 1, get the news articles
if abs(diff_percent) > 1:
    news_params = {"apiKey": NEWS_API_KEY, "qInTitle": COMPANY_NAME}
    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    articles = news_response.json()["articles"]
    three_articles = articles[:3]

    # Format the articles
    formatted_articles = [
        [
            f"{STOCK_NAME}: {up_down}{diff_percent}% \nHeadline: {article['title']}. \nBrief: {article['description']}"
        ]
        for article in three_articles
    ]

    # Send the formatted articles as SMS messages
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    for article in formatted_articles:
        message = client.messages.create(
            body=article, from_="+18147396865", to="+34619931313"
        )
