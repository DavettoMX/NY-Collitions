import pip
pip.main(["install","plotly.express"])
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = (
"data/Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Motor Vehile Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used "
"to analyze motor vehicle collisions in NYC")

@st.cache(persist=True)
def load_data(rows):
    data = pd.read_csv(DATA_URL, nrows=rows, parse_dates=[['CRASH DATE', 'CRASH TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True) # lowercase all column names
    data.rename(columns={'crash date_crash time': 'date/time', 'number of persons injured': 'injured_persons'}, inplace=True)
    return data

data = load_data(100000)
original_data = data

# Visualize 2D map
st.header("Where are the most people Injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))


# Visualize 3D map
st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 15,
        "pitch": 70,
    },
    layers = [
        pdk.Layer(
            "HexagonLayer",
            data = data[['date/time', 'latitude', 'longitude']],
            get_position = ['longitude', 'latitude'],
            radius = 100,
            extruded = True,
            pickable = True,
            elevation_scale = 4,
            elevation_range = [0, 1000],
        ),
    ],
))

# Most Common Vehicle Types
st.header("The most common vehicle types in collisions")
px.bar(data, x='vehicle type code 2', y='injured_persons', color='vehicle type code 1', height=600)

if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
