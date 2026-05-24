import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data():
    # Read the CR1000X data file, skipping metadata rows (rows 0, 2, 3)
    # Row 1 contains the column names (TIMESTAMP, RECORD, etc.)
    df = pd.read_csv('CR1000X_Hazeva_Lys_DendroData.dat', skiprows=[0, 2, 3])
    
    # Convert TIMESTAMP column to datetime
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
    df = df.rename(columns={'TIMESTAMP': 'datetime'})
    
    # Extract frequency columns (Dend_freq 1-12, columns O-Z)
    freq_cols = [col for col in df.columns if col.startswith('Dend_freq')]
    
    # Extract inductance columns (Dend_Induct 1-12, columns AA-AL)
    induct_cols = [col for col in df.columns if col.startswith('Dend_Induct')]
    
    # Convert to numeric and remove -1 and 0 values as NaN
    for col in freq_cols + induct_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df.loc[(df[col] == -1) | (df[col] == 0), col] = pd.NA
    
    return df, freq_cols, induct_cols

df, freq_cols, induct_cols = load_data()

st.title("Dendrometer Data Visualization")

# Create sensor list (1-12)
num_sensors = len(freq_cols)
sensor_ids = list(range(1, num_sensors + 1))

# Sidebar for sensor selection
with st.sidebar:
    st.title("⚙️ Filter Settings")
    selected_sensors = st.multiselect("Select Sensors", sensor_ids, default=[1])
    
    st.subheader("Time Range")
    # Default to 1 week ago from the latest data point
    default_start = (pd.to_datetime(df['datetime'].max()).date() - pd.Timedelta(days=7))
    start_date = st.date_input("Start Date", value=default_start)
    
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

# Filter data for selected sensors and time range
if selected_sensors:
    # Select relevant columns for the chosen sensors
    selected_freq_cols = [freq_cols[i-1] for i in selected_sensors if i <= len(freq_cols)]
    selected_induct_cols = [induct_cols[i-1] for i in selected_sensors if i <= len(induct_cols)]
    
    sensor_data = df[['datetime'] + selected_freq_cols + selected_induct_cols].copy()
    sensor_data = sensor_data.sort_values('datetime')
    
    # Filter by time range
    sensor_data = sensor_data[(sensor_data['datetime'].dt.date >= start_date) & (sensor_data['datetime'].dt.date <= end_date)]
    
    # Calculate inductance change in PPM relative to first measurement in selected period
    ppm_cols = []
    if not sensor_data.empty:
        for sensor_id, induct_col in zip(selected_sensors, selected_induct_cols):
            ppm_col_name = f'Induct_Change_PPM_Sensor_{sensor_id}'
            ppm_cols.append(ppm_col_name)
            
            # Get first non-NaN value
            first_valid_value = sensor_data[induct_col].dropna().iloc[0] if len(sensor_data[induct_col].dropna()) > 0 else None
            
            if first_valid_value is not None and first_valid_value != 0:
                # Calculate PPM change: ((current - first) / first) * 1e6
                sensor_data[ppm_col_name] = ((sensor_data[induct_col] - first_valid_value) / first_valid_value) * 1e6
            else:
                sensor_data[ppm_col_name] = pd.NA
else:
    sensor_data = pd.DataFrame()  # Empty if none selected
    ppm_cols = []

# Parameters to plot
parameters = {
    'Frequency [Hz]': 'Frequency [Hz]',
    'Inductance [H]': 'Inductance [H]'
}

# Create plots
if not sensor_data.empty:
    st.subheader("Dendrometer Sensor Data")
    # Tabs for Frequency, Inductance, and PPM Change
    tab1, tab2, tab3 = st.tabs(["Frequency [Hz]", "Inductance [H]", "Inductance Change [PPM]"])
    
    with tab1:
        st.write("**Frequency measurements for selected sensors**")
        # Create a line plot for each selected sensor
        fig = go.Figure()
        for idx, sensor_id in enumerate(selected_sensors):
            col_name = freq_cols[sensor_id - 1]
            plot_data = sensor_data[['datetime', col_name]].dropna()
            if not plot_data.empty:
                fig.add_trace(go.Scatter(
                    x=plot_data['datetime'],
                    y=plot_data[col_name],
                    mode='lines',
                    name=f'Sensor {sensor_id}',
                    line=dict(width=2)
                ))
        
        if len(fig.data) > 0:
            fig.update_layout(
                title='Frequency [Hz] vs Time',
                xaxis_title='Time',
                yaxis_title='Frequency [Hz]',
                hovermode='x unified',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No frequency data available for selected sensors in this time range")
    
    with tab2:
        st.write("**Inductance measurements for selected sensors**")
        # Create a line plot for each selected sensor
        fig = go.Figure()
        for idx, sensor_id in enumerate(selected_sensors):
            col_name = induct_cols[sensor_id - 1]
            plot_data = sensor_data[['datetime', col_name]].dropna()
            if not plot_data.empty:
                fig.add_trace(go.Scatter(
                    x=plot_data['datetime'],
                    y=plot_data[col_name],
                    mode='lines',
                    name=f'Sensor {sensor_id}',
                    line=dict(width=2)
                ))
        
        if len(fig.data) > 0:
            fig.update_layout(
                title='Inductance [H] vs Time',
                xaxis_title='Time',
                yaxis_title='Inductance [H]',
                hovermode='x unified',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No inductance data available for selected sensors in this time range")
    
    with tab3:
        st.write("**Inductance change in PPM relative to first measurement in selected period**")
        # Create a line plot for each selected sensor's PPM change
        fig = go.Figure()
        for idx, (sensor_id, ppm_col) in enumerate(zip(selected_sensors, ppm_cols)):
            plot_data = sensor_data[['datetime', ppm_col]].dropna()
            if not plot_data.empty:
                fig.add_trace(go.Scatter(
                    x=plot_data['datetime'],
                    y=plot_data[ppm_col],
                    mode='lines',
                    name=f'Sensor {sensor_id}',
                    line=dict(width=2)
                ))
        
        if len(fig.data) > 0:
            fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Baseline")
            fig.update_layout(
                title='Inductance Change [PPM] vs Time',
                xaxis_title='Time',
                yaxis_title='Change [PPM]',
                hovermode='x unified',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No inductance change data available for selected sensors in this time range")
    
    # Display data summary
    st.subheader("Data Summary")
    summary_data = sensor_data.describe().round(6)
    st.dataframe(summary_data)
else:
    st.write("Please select at least one sensor.")
