import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    # Combine Date and Time into datetime
    df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    # Handle "No response" as NaN
    df.replace('No response', pd.NA, inplace=True)
    df.replace('N/A', pd.NA, inplace=True)
    # Convert numeric columns
    numeric_cols = ['Frequancy [Hz]', 'Inductance [H]', 'Change [PPM]', 'Temperatur [C]', 'Humidity [%]']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Add MDS and TDV indices (placeholders for now)
    df['MDS'] = 0  # Will be updated with actual calculations
    df['TDV'] = 0  # Will be updated with actual calculations
    
    return df

df = load_data()

st.title("Dendrometer Data Visualization")

# Get unique sensor IDs
sensor_ids = sorted(df['Sensor ID'].unique())

# Sidebar for sensor selection
with st.sidebar:
    st.title("⚙️ Filter Settings")
    selected_sensors = st.multiselect("Select Sensor IDs", sensor_ids, default=sensor_ids[:1])  # Default to first sensor
    
    st.subheader("Time Range")
    start_date = st.date_input("Start Date", value=pd.to_datetime(df['datetime'].min()).date())
    
    range_type = st.radio("Range Type", ["Fixed Period", "Custom Date"])
    
    if range_type == "Fixed Period":
        period_option = st.selectbox("Select Period", ["1 Day", "5 Days", "1 Week", "2 Weeks", "1 Month"])
        if period_option == "1 Day":
            end_date = start_date + pd.Timedelta(days=1)
        elif period_option == "5 Days":
            end_date = start_date + pd.Timedelta(days=5)
        elif period_option == "1 Week":
            end_date = start_date + pd.Timedelta(weeks=1)
        elif period_option == "2 Weeks":
            end_date = start_date + pd.Timedelta(weeks=2)
        elif period_option == "1 Month":
            end_date = (start_date + pd.DateOffset(months=1)).date()
        st.write(f"**Time Range:** {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
    else:  # Custom Date
        end_date = st.date_input("End Date", value=pd.to_datetime(df['datetime'].max()).date(), min_value=start_date)

# Filter data for selected sensors
if selected_sensors:
    sensor_data = df[df['Sensor ID'].isin(selected_sensors)].copy()
    sensor_data = sensor_data.sort_values('datetime')
    
    # Filter by time range
    sensor_data = sensor_data[(sensor_data['datetime'].dt.date >= start_date) & (sensor_data['datetime'].dt.date <= end_date)]
else:
    sensor_data = pd.DataFrame()  # Empty if none selected

# Parameters to plot
parameters = {
    'Frequancy [Hz]': 'Frequency [Hz]',
    'Inductance [H]': 'Inductance [H]',
    'Change [PPM]': 'Change [PPM]',
    'Temperatur [C]': 'Temperature [C]',
    'Humidity [%]': 'Humidity [%]'
}

# Create plots
if not sensor_data.empty:
    st.subheader("Dendrometer Parameters")
    # Tabs for Frequency, Inductance, and Change
    tab1, tab2, tab3 = st.tabs(["Frequency", "Inductance", "Change"])
    
    with tab1:
        col = 'Frequancy [Hz]'
        label = 'Frequency [Hz]'
        plot_data = sensor_data[sensor_data[col].notna()]
        if not plot_data.empty:
            fig = px.line(plot_data, x='datetime', y=col, color='Sensor ID', title=f'{label} vs Time')
            fig.update_layout(xaxis_title='Time', yaxis_title=label)
            st.plotly_chart(fig)
        else:
            st.write(f"No data available for {label} in selected sensors")
    
    with tab2:
        col = 'Inductance [H]'
        label = 'Inductance [H]'
        plot_data = sensor_data[sensor_data[col].notna()]
        if not plot_data.empty:
            fig = px.line(plot_data, x='datetime', y=col, color='Sensor ID', title=f'{label} vs Time')
            fig.update_layout(xaxis_title='Time', yaxis_title=label)
            st.plotly_chart(fig)
        else:
            st.write(f"No data available for {label} in selected sensors")
    
    with tab3:
        col = 'Change [PPM]'
        label = 'Change [PPM]'
        plot_data = sensor_data[sensor_data[col].notna()]
        if not plot_data.empty:
            fig = px.line(plot_data, x='datetime', y=col, color='Sensor ID', title=f'{label} vs Time')
            fig.update_layout(xaxis_title='Time', yaxis_title=label)
            st.plotly_chart(fig)
        else:
            st.write(f"No data available for {label} in selected sensors")
    
    st.subheader("Environmental Parameters")
    # Tabs for Temperature and Humidity
    tab4, tab5 = st.tabs(["Temperature", "Humidity"])
    
    with tab4:
        col = 'Temperatur [C]'
        label = 'Temperature [C]'
        plot_data = sensor_data[sensor_data[col].notna()]
        if not plot_data.empty:
            fig = px.line(plot_data, x='datetime', y=col, color='Sensor ID', title=f'{label} vs Time')
            fig.update_layout(xaxis_title='Time', yaxis_title=label)
            st.plotly_chart(fig)
        else:
            st.write(f"No data available for {label} in selected sensors")
    
    with tab5:
        col = 'Humidity [%]'
        label = 'Humidity [%]'
        plot_data = sensor_data[sensor_data[col].notna()]
        if not plot_data.empty:
            fig = px.line(plot_data, x='datetime', y=col, color='Sensor ID', title=f'{label} vs Time')
            fig.update_layout(xaxis_title='Time', yaxis_title=label)
            st.plotly_chart(fig)
        else:
            st.write(f"No data available for {label} in selected sensors")
else:
    st.write("Please select at least one sensor ID.")
