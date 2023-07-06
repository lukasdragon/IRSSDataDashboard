import json

import requests
import streamlit as st
import numpy as np

from datetime import datetime

api_url = "https://hacvffgmaquyyeiusnbi.supabase.co/rest/v1/"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYm" \
          "FzZSIsInJlZiI6ImhhY3ZmZmdtYXF1eXllaXVzbmJpIiwicm9sZSI6Im" \
          "Fub24iLCJpYXQiOjE2ODczMDI5NDQsImV4cCI6MjAwMjg3ODk0NH0." \
          "HIO6RGgmEtBD7JaSvNEM5EX2C-EbVQH8ZmjHIExD53Q"


# API_Key is public; No private data is exposed.


def unix_ms_to_datetime(millis):
    """
    Convert unix time in milliseconds to a datetime object.

    Args:
        millis (int): Unix time in milliseconds.

    Returns:
        datetime.datetime: A datetime object representing the given unix time.
    """
    return datetime.fromtimestamp(millis / 1000.0)  # Divide by 1000 to convert to seconds


def format_url_params(*params):
    """
       Concatenates all input parameters with "&" for URL formatting.

       :type params: str
       :return: a string concatenated with "&"
       """
    return '&'.join(params)


@st.cache_data
def make_request(path, *params):
    """
       Makes a GET request to the API.

       The function concatenates the API url, path, apikey, and any extra parameters
       to form the complete URL, then makes a GET request to that URL.

       If the request is successful, the function returns the response in JSON format.

       :param path: The API endpoint.
       :param params: Extra parameters to add to the API URL.
       :return: The response in JSON format.
       """

    param_string = format_url_params(*params)
    url = f"{api_url}{path}?apikey={api_key}&{param_string}"

    response = requests.get(url)

    if response.ok:
        return response.json()
    else:
        return response.json()


channels = make_request("channels")
usernames = make_request("usernames")
rolls = make_request("rolls", "select=unix_milliseconds, dice_value"
                              "channel:channels(name:channel_name),"
                              "user:usernames(name:username)")

for roll in rolls:
    roll["date_time"] = unix_ms_to_datetime(roll["unix_milliseconds"])
