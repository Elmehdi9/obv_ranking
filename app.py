import streamlit as st
import pandas as pd
from datetime import datetime

# Load data from CSV
@st.cache_data
def load_data():
    return pd.read_csv('data/players_stats.csv')

df = load_data()

# Calculate age from birth date
def calculate_age(birth_date):
    try:
        birth_date = str(birth_date)
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except (ValueError, TypeError):
        return None

df['age'] = df['birth_date'].apply(calculate_age)

# Drop rows with invalid age values
df = df.dropna(subset=['age'])

# Define initial weights for OBV ranking
obv_weights = {
    'Striker': [50, 35, 15],
    'Attacking Midfielder/Winger': [30, 40, 30],
    'Midfielder': [15, 35, 50],
    'Center Back': [0, 30, 70],
    'Full Back': [10, 60, 30]
}

# Define initial weights for Defensive Index
defensive_weights = {
    'Striker': [80, 20],
    'Attacking Midfielder/Winger': [70, 30],
    'Midfielder': [50, 50],
    'Full Back': [40, 60],
    'Center Back': [30, 70]
}

# Mapping detailed positions to simplified categories
position_mapping = {
    'Centre Attacking Midfielder': 'Attacking Midfielder/Winger',
    'Left Midfielder': 'Midfielder',
    'Right Defensive Midfielder': 'Midfielder',
    'Right Midfielder': 'Midfielder',
    'Left Back': 'Full Back',
    'Centre Defensive Midfielder': 'Midfielder',
    'Left Centre Forward': 'Striker',
    'Left Centre Midfielder': 'Midfielder',
    'Right Centre Midfielder': 'Midfielder',
    'Left Attacking Midfielder': 'Attacking Midfielder/Winger',
    'Centre Forward': 'Striker',
    'Left Defensive Midfielder': 'Midfielder',
    'Right Wing': 'Attacking Midfielder/Winger',
    'Right Centre Back': 'Center Back',
    'Right Back': 'Full Back',
    'Left Centre Back': 'Center Back',
    'Left Wing': 'Attacking Midfielder/Winger',
    'Goalkeeper': 'Goalkeeper',
    'Right Centre Forward': 'Striker',
    'Right Wing Back': 'Full Back',
    'Left Wing Back': 'Full Back',
    'Centre Back': 'Center Back',
    'Right Attacking Midfielder': 'Attacking Midfielder/Winger'
}

# Apply position mapping to the DataFrame
df['simplified_position'] = df['primary_position'].map(position_mapping)

with st.sidebar:
    mode = st.radio(
        "Application",
        ["OBV ranking", "Defensive Index"],
        index=None,
    )

    # Filter by age
    min_age, max_age = st.slider('Select Age Range', 18, 40, (18, 40))
    df = df[(df['age'] >= min_age) & (df['age'] <= max_age)]

    # Filter by minutes played
    min_minutes, max_minutes = st.slider('Select Minutes Played Range', 0, 3000, (0, 3000))
    df = df[(df['player_season_minutes'] >= min_minutes) & (df['player_season_minutes'] <= max_minutes)]

weights = []
if mode == 'OBV ranking':
    st.sidebar.write("Select Position for OBV ranking:")
    position = st.sidebar.selectbox("Position", ['Striker', 'Attacking Midfielder/Winger', 'Midfielder', 'Center Back', 'Full Back'])
    weights = obv_weights[position]
    st.sidebar.write("Adjust Weights:")
    
    weight1 = st.sidebar.slider('OBV Shot 90', 0, 100, weights[0], key='weight1')
    weight2 = st.sidebar.slider('OBV Dribble Carry 90', 0, 100, weights[1], key='weight2')
    weight3 = st.sidebar.slider('OBV Pass 90', 0, 100, 100 - weight1 - weight2, key='weight3')
    
    if weight1 + weight2 + weight3 != 100:
        st.sidebar.warning('The sum of the weights must be 100. Adjusting the last weight.')
        weight3 = 100 - weight1 - weight2

    weights = [weight1, weight2, weight3]

    # Filter the DataFrame based on the selected position
    filtered_df = df[df['simplified_position'] == position]

    filtered_df['index'] = filtered_df['player_season_obv_shot_90'] * weights[0] / 100 + filtered_df['player_season_obv_dribble_carry_90'] * weights[1] / 100 + filtered_df['player_season_obv_pass_90'] * weights[2] / 100
    ranked_df = filtered_df[['player_name', 'team_name', 'primary_position', 'birth_date', 'player_season_minutes','player_season_obv_shot_90','player_season_obv_dribble_carry_90', 'player_season_obv_pass_90','index']].sort_values(by='index', ascending=False).reset_index(drop= True)
    st.write(round(ranked_df, 2))

elif mode == 'Defensive Index':
    st.sidebar.write("Select Position for Defensive Index:")
    position = st.sidebar.selectbox("Position", ['Striker', 'Attacking Midfielder/Winger', 'Midfielder', 'Center Back', 'Full Back'])
    weights = defensive_weights[position]
    st.sidebar.write("Adjust Weights:")
    
    weight1 = st.sidebar.slider('Padj Interceptions 90', 0, 100, weights[0], key='def_weight1')
    weight2 = st.sidebar.slider('Padj Pressures 90', 0, 100, 100 - weight1, key='def_weight2')
    
    if weight1 + weight2 != 100:
        st.sidebar.warning('The sum of the weights must be 100. Adjusting the last weight.')
        weight2 = 100 - weight1

    weights = [weight1, weight2]

    # Filter the DataFrame based on the selected position
    filtered_df = df[df['simplified_position'] == position]

    filtered_df['index'] = filtered_df['player_season_padj_interceptions_90'] * weights[0] / 100 + filtered_df['player_season_padj_pressures_90'] * weights[1] / 100
    ranked_df = filtered_df[['player_name', 'team_name', 'primary_position', 'birth_date', 'player_season_minutes', 'player_season_padj_interceptions_90','player_season_padj_pressures_90', 'index']].sort_values(by='index', ascending=False).reset_index(drop= True)
    st.write(round(ranked_df, 2))
