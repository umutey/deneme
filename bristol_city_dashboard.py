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

# Create the pitch
fig = go.Figure()

# Add pitch layout
fig.add_shape(type="rect", x0=0, y0=0, x1=105, y1=68, line=dict(color="black", width=2))
fig.add_shape(type="circle", x0=52.5 - 9.15, y0=34 - 9.15, x1=52.5 + 9.15, y1=34 + 9.15, line=dict(color="black", width=2))
fig.add_shape(type="line", x0=52.5, y0=0, x1=52.5, y1=68, line=dict(color="black", width=2))

# Add penalty areas
fig.add_shape(type="rect", x0=0, y0=22.32, x1=16.5, y1=45.68, line=dict(color="black", width=2))
fig.add_shape(type="rect", x0=105, y0=22.32, x1=88.5, y1=45.68, line=dict(color="black", width=2))

# Add player positions
fig.add_trace(go.Scatter(
    x=filtered_data["x_position"],
    y=filtered_data["y_position"],
    mode="markers+text",
    marker=dict(size=10, color="blue"),
    text=filtered_data["short_name"],  # Display player name
    textposition="top center",
    hovertemplate=(
        "<b>%{text}</b><br>" +
        "Position: %{customdata[0]}<br>" +
        "Status: %{customdata[1]}<br>" +
        "Market Value: €%{customdata[2]:,.2f}<br>" +
        "<extra></extra>"
    ),
    customdata=filtered_data[["general_position", "status", "value_eur"]].values  # Add additional info
))

# Update layout
fig.update_layout(
    title="Interactive Bristol City FC Pitch",
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    height=500,
    width=800,
    showlegend=False
)

# Render the pitch in Streamlit
st.plotly_chart(fig)


# Player Stats Table
st.markdown("### Player Stats")
st.dataframe(
    filtered_data[
        ["short_name", "general_position", "status", "nationality_name", "value_eur", "pace", "shooting"]
    ].sort_values(by="value_eur", ascending=False)
)
