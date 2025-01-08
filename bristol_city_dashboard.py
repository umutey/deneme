import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
from matplotlib.patches import Circle, Rectangle, Arc
import matplotlib.pyplot as plt

# Load Data
starting_11 = pd.read_csv("bristol_city_starting_11.csv")
bench = pd.read_csv("bristol_city_bench.csv")

# Merge datasets with an indicator for group
starting_11['status'] = 'Starting 11'
bench['status'] = 'Bench'
players_data = pd.concat([starting_11, bench], ignore_index=True)

# Sidebar Filters
st.sidebar.title("Bristol City FC Dashboard")
selected_status = st.sidebar.multiselect(
    "Select Group", 
    players_data["status"].unique(), 
    default=players_data["status"].unique()
)
selected_position = st.sidebar.multiselect(
    "Select Position(s)", 
    players_data["general_position"].unique(),
    default=players_data["general_position"].unique()
)
selected_nationality = st.sidebar.multiselect(
    "Select Nationality", 
    players_data["nationality_name"].unique(),
    default=players_data["nationality_name"].unique()
)

# Filter Data
filtered_data = players_data[
    (players_data["status"].isin(selected_status)) &
    (players_data["general_position"].isin(selected_position)) &
    (players_data["nationality_name"].isin(selected_nationality))
]

# Filter Data
filtered_data = players_data[
    (players_data["status"].isin(selected_status)) &
    (players_data["general_position"].isin(selected_position)) &
    (players_data["nationality_name"].isin(selected_nationality))
]

from itertools import cycle

# Define position coordinates for a 3-4-3 formation
position_coordinates = {
    "GK": cycle([(5, 34)]),  # Goalkeeper
    "CB": cycle([(25, 20), (25, 34), (25, 48)]),  # Center Backs
    "MID": cycle([(50, 10), (50, 24), (50, 44), (50, 58)]),  # Midfielders
    "FWD": cycle([(75, 24), (75, 34), (75, 44)])  # Forwards
}

# Assign coordinates to players based on their general position
def get_position_coordinates(player_position):
    # Extract primary position
    primary_position = player_position.split(',')[0].strip()
    if primary_position == "GK":
        return next(position_coordinates["GK"])
    elif primary_position in ["ST", "LW", "RW", "CF"]:
        return next(position_coordinates["FWD"])
    elif primary_position in ["CB", "LB", "RB"]:
        return next(position_coordinates["CB"])
    elif primary_position in ["CM", "CDM", "CAM", "LM", "RM"]:
        return next(position_coordinates["MID"])
    else:
        return (0, 0)  # Default position for undefined roles

# Apply the mapping to create new columns for x and y coordinates
filtered_data["x_position"], filtered_data["y_position"] = zip(
    *filtered_data["player_positions"].apply(get_position_coordinates)
)

# Debug: Check the generated positions
st.write("Player positions with coordinates:", filtered_data[["short_name", "player_positions", "x_position", "y_position"]].head())


# Main Dashboard
st.title("Bristol City FC Team Dashboard")
st.markdown("### Overview")
st.metric("Total Players", len(filtered_data))
st.metric("Average Market Value (€M)", filtered_data["value_eur"].mean().round(2))

# Nationality Visualization on Map
st.markdown("### Player Nationalities")
# Nationality Visualization on Map
st.markdown("### Player Nationalities")
import requests
import json

# Load GeoJSON data from an online source
url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
world = gpd.read_file(url)  # Directly pass the URL to read GeoJSON data

# Merge player data with world GeoJSON data (if needed for further customization)
fig = px.scatter_geo(
    filtered_data,  # Corrected the data source to use filtered_data directly
    lat="latitude", 
    lon="longitude", 
    hover_name="short_name",
    title="Player Nationalities", 
    size="value_eur", 
    projection="natural earth"
)
st.plotly_chart(fig)


# Football Pitch and Player Positions
st.markdown("### Player Positions on the Pitch")
fig, ax = plt.subplots(figsize=(10, 7))

# Draw the pitch
def draw_pitch(ax=None):
    pitch = Rectangle([0, 0], width=105, height=68, fill=False, color="black")
    center_circle = Circle([52.5, 34], radius=9.15, fill=False, color="black")
    center_spot = Circle([52.5, 34], radius=0.37, fill=True, color="black")
    penalty_arc_left = Arc([11, 34], height=18.3, width=18.3, angle=0, theta1=308, theta2=52, color="black")
    penalty_arc_right = Arc([94, 34], height=18.3, width=18.3, angle=0, theta1=128, theta2=232, color="black")
    
    for element in [pitch, center_circle, center_spot, penalty_arc_left, penalty_arc_right]:
        ax.add_patch(element)

    ax.set_xlim(-5, 110)
    ax.set_ylim(-5, 73)
    ax.axis("off")

draw_pitch(ax)

# Plot players
for _, row in filtered_data.iterrows():
    ax.text(row["x_position"], row["y_position"], row["short_name"], fontsize=8, ha='center', color="blue")

st.pyplot(fig)

# Player Stats Table
st.markdown("### Player Stats")
st.dataframe(
    filtered_data[
        ["short_name", "general_position", "status", "nationality_name", "value_eur", "pace", "shooting"]
    ].sort_values(by="value_eur", ascending=False)
)
