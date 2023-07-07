import json
import requests
import streamlit as st
import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime

API_URL = "https://hacvffgmaquyyeiusnbi.supabase.co/rest/v1/"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYm" \
          "FzZSIsInJlZiI6ImhhY3ZmZmdtYXF1eXllaXVzbmJpIiwicm9sZSI6Im" \
          "Fub24iLCJpYXQiOjE2ODczMDI5NDQsImV4cCI6MjAwMjg3ODk0NH0." \
          "HIO6RGgmEtBD7JaSvNEM5EX2C-EbVQH8ZmjHIExD53Q"  # replace with your actual API Key


def unix_ms_to_datetime(millis):
    return datetime.fromtimestamp(millis / 1000.0)


def date_to_unix_ms(date):
    dt = datetime(date.year, date.month, date.day)
    return int(dt.timestamp() * 1000)


def make_request(path, *params):
    param_string = '&'.join(params)
    url = f"{API_URL}{path}"
    headers = {'apikey': API_KEY}
    response = requests.get(url, params=param_string, headers=headers)

    if response.ok:
        return response.json()
    else:
        return response.json()


def get_date_of_previous_sunday(weeks_before: int = 1) -> date:
    today = date.today()
    date_weeks_before = today - timedelta(weeks=weeks_before)
    days_to_subtract = (date_weeks_before.weekday() + 1) % 7
    previous_sunday = date_weeks_before - timedelta(days=days_to_subtract)
    return previous_sunday


sunday = get_date_of_previous_sunday(2)
ums = date_to_unix_ms(sunday)

rolls = make_request("rolls",
                     "select=unix_milliseconds,dice_value,"
                     "channel:channels(name:channel_name),"
                     "username:usernames(name:username)",
                     f"unix_milliseconds=gt.{ums}")

df = pd.DataFrame(rolls)

df["date_time"] = pd.to_datetime(df["unix_milliseconds"], unit='ms')
df["channel"] = df["channel"].apply(lambda x: x['name'])
df["username"] = df["username"].apply(lambda x: x['name'])

df.set_index('date_time', inplace=True)

df.sort_index(inplace=True)


# Create a new column with mean dice_value
df['mean'] = np.mean(df['dice_value'])

st.write("[API Documentation](https://app.swaggerhub.com/apis/OLSON_1/JavaJotterAPI/10.2.0)")

# Use Streamlit to plot the data
st.line_chart(df[['dice_value', 'mean']])


st.write(df)
