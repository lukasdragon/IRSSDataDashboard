import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import footer
from datetime import datetime, timedelta

st.set_page_config(page_title="Java Jotter Dashboard", page_icon="☕", layout="centered",
                   initial_sidebar_state="expanded", menu_items={
                    'Get Help': 'https://github.com/lukasdragon/IRSSDataDashboard',
                    'Report a bug': "https://github.com/lukasdragon/IRSSDataDashboard/issues",
                    })

footer.footer()

API_URL = "https://hacvffgmaquyyeiusnbi.supabase.co/rest/v1/"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYm" \
          "FzZSIsInJlZiI6ImhhY3ZmZmdtYXF1eXllaXVzbmJpIiwicm9sZSI6Im" \
          "Fub24iLCJpYXQiOjE2ODczMDI5NDQsImV4cCI6MjAwMjg3ODk0NH0." \
          "HIO6RGgmEtBD7JaSvNEM5EX2C-EbVQH8ZmjHIExD53Q"
HEADERS = {'apikey': API_KEY}

with st.sidebar:
    st.title("Java Jotter Dashboard")
    st.write(
        "This dashboard analyses dice roll data between the given dates. "
        "In the IRSS, each member who drinks coffee must roll a dice. "
        "The lowest roller on each day has to make the coffee for the next morning. "
        "Data is scrapped in near-realtime through our JavaJotter bot.")


def make_request(path, *params):
    url = f"{API_URL}{path}?{'&'.join(params)}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Request failed with status code {response.status_code}: {response.text}")


def get_date_of_previous_sunday(input_date, weeks_before=1):
    date_weeks_before = input_date - timedelta(weeks=weeks_before)
    days_to_subtract = (date_weeks_before.weekday() + 1) % 7
    return date_weeks_before - timedelta(days=days_to_subtract)


def date_to_unix_ms(date):
    """Convert date to unix timestamp in ms"""
    dt = datetime(date.year, date.month, date.day)
    return int(dt.timestamp() * 1000)


@st.cache_data
def fetch_and_process_data(start_date, end_date):
    start_ums = date_to_unix_ms(start_date)
    end_ums = date_to_unix_ms(end_date)
    rolls = make_request("rolls",
                         "select=unix_milliseconds,dice_value,"
                         "channel:channels(name:channel_name),"
                         "username:usernames(name:username)",
                         f"unix_milliseconds=gte.{start_ums}",
                         f"unix_milliseconds=lte.{end_ums}")

    if rolls:
        df = pd.DataFrame(rolls)
        df["date_time"] = pd.to_datetime(df["unix_milliseconds"], unit='ms')
        df["channel"] = df["channel"].apply(lambda x: x['name'])
        df["username"] = df["username"].apply(lambda x: x['name'])
        df.set_index('date_time', inplace=True)
        df.sort_index(inplace=True)

        # Calculate the minimum dice roll per day
        min_roll_index = df.groupby(df.index.date)['dice_value'].idxmin()
        df_min_daily_roll = df.loc[min_roll_index]

        st.write(df.describe())  # Descriptive statistics
        st.dataframe(df)  # Display the full dataframe in the app
        st.dataframe(df_min_daily_roll)  # Display the dataframe of minimum daily rolls
        return df, df_min_daily_roll
    else:
        st.error('Error: Unable to retrieve data.')
        return None, None


def plot(df, df_min):
    plot_pie(df_min)
    plot_line(df)
    plot_hist(df)
    plot_heatmap(df)


def plot_pie(df):
    username_counts = df['username'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(username_counts, labels=username_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title('Distribution of coffee preparers over time period.')
    st.pyplot(fig)


def plot_line(df):
    st.line_chart(df[['dice_value']])


def plot_hist(df):
    fig, ax = plt.subplots()
    df['dice_value'].plot(kind='hist', rwidth=0.8, bins=6)
    plt.title('Dice roll frequencies')
    st.pyplot(fig)


def plot_heatmap(df):
    df['weekday'] = df.index.weekday
    heatmap_data = df.groupby(['weekday', 'username']).size().reset_index()
    heatmap_data.columns = ['weekday', 'username', 'count']
    heatmap_data = heatmap_data.pivot('username', 'weekday', 'count')
    fig, ax = plt.subplots()
    sns.heatmap(heatmap_data, cmap="YlGnBu")
    plt.title('Roll counts by day of week and user')
    st.pyplot(fig)


start_date = get_date_of_previous_sunday(datetime.today(), 4)
end_date = datetime.today()

with st.sidebar:
    dates = st.date_input('Select start and end date:', [start_date, end_date])
    button = st.button('Confirm Dates')
if button:
    if len(dates) < 2:  # If the user did not select a second date
        st.warning('Please select a second date.')
    elif dates[0] > dates[1]:
        st.error('Error: End date must fall after start date.')
    else:
        start_date, end_date = dates
        end_date += timedelta(days=1)  # make end_date inclusive
        df, df_min = fetch_and_process_data(start_date, end_date)
        if df is not None:
            plot(df, df_min)

# footer("[API Documentation](https://app.swaggerhub.com/apis/OLSON_1/JavaJotterAPI/10.2.0)")
