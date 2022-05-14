import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

DATA_URL = (
"data/Motor_Vehicle_Collisions_Crashes.csv"
)

st.title("Motor Vehile Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used "
"to analyze motor vehicle collisions in NYC")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    try:
        data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    except KeyError:
        pass
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

data = load_data(80_000)
original_data = data

st.header("Where are the most people Injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))


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
        "zoom": 11,
        "pitch": 50,
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

st.header("Top 5 Dangerous Streets by Affected Type")
select = st.selectbox('Affected Type of People', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by = ["injured_pedestrians"], ascending = False).dropna(how = 'any')[:5])
elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by = ["injured_cyclists"], ascending = False).dropna(how = 'any')[:5])
else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by = ["injured_motorists"], ascending = False).dropna(how = 'any')[:5])


if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
