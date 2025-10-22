import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# --- 1. GLOBAL CONFIGURATION & API BASE URL ---


API_BASE_URL = "http://localhost:8080"
SALES_ENDPOINT = "api/v1/products/sales_detail" # Placeholder for your specific sales endpoint

st.set_page_config(
    page_title="Product Data Analysis Dashboard (Pandas/Streamlit)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. API CONNECTION AND CACHING FUNCTION ---

# st.cache_data stores the function result. If arguments don't change,
# it won't call the API again.
@st.cache_data(ttl=600) # ttl=600 means data will refresh every 10 minutes
def fetch_data_from_api(endpoint):
    """Fetches data from the Spring Boot API and converts it to a Pandas DataFrame."""
    full_url = f"{API_BASE_URL}/{endpoint}" # Correct URL construction
    try:
        # GET request to the specific endpoint
        response = requests.get(full_url)
        response.raise_for_status() # Raises an exception for 4xx or 5xx status codes
        data = response.json()
        
        # Convert the list of JSON objects to a Pandas DataFrame
        df = pd.DataFrame(data)
        
        # Data Processing: Ensure 'revenue' is numeric and 'date' is datetime
        if 'ingresos' in df.columns: # Keep 'ingresos' if that's the column name from API
            df['revenue'] = pd.to_numeric(df['ingresos'], errors='coerce')
        if 'fecha' in df.columns: # Keep 'fecha' if that's the column name from API
            df['date'] = pd.to_datetime(df['fecha'], errors='coerce') 
            df['month_name'] = df['date'].dt.strftime('%B') # Month name
            df['year'] = df['date'].dt.year
            
        # Select and rename columns for clarity in the rest of the script
        if 'producto' in df.columns and 'categoria' in df.columns:
             df = df.rename(columns={'producto': 'product', 'categoria': 'category'})

        return df
        
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error connecting to API ({full_url}): {e}")
        return pd.DataFrame() # Returns an empty DataFrame on error

# --- 3. DATA SIMULATION FUNCTION ---
# This function allows the app to run if the API is not ready
def get_simulated_data():
    data = {
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'product': ['Whole Milk', 'Fresh Cheese', 'Oats', 'Rice', 'Yogurt', 
                     'Butter', 'Lentils', 'Beans', 'Cream', 'Barley'],
        'category': ['Dairy', 'Dairy', 'Grain', 'Grain', 'Dairy', 
                      'Dairy', 'Grain', 'Grain', 'Dairy', 'Grain'],
        'revenue': [1200, 850, 400, 300, 750, 500, 250, 150, 600, 100],
        # Simulated dates for monthly analysis
        'date': [
            datetime(2025, 9, 15), datetime(2025, 10, 5), datetime(2025, 10, 10), 
            datetime(2025, 9, 20), datetime(2025, 10, 1), datetime(2025, 9, 25), 
            datetime(2025, 10, 12), datetime(2025, 9, 28), datetime(2025, 10, 3), 
            datetime(2025, 10, 11)
        ]
    }
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['month_name'] = df['date'].dt.strftime('%B')
    df['year'] = df['date'].dt.year
    return df
# --- END OF SIMULATION ---


# --- MAIN APPLICATION CODE ---

# 1. Data Loading (Use API or simulation if API fails)
df_sales = fetch_data_from_api(SALES_ENDPOINT) 

if df_sales.empty or 'revenue' not in df_sales.columns:
    st.warning("⚠️ Using Simulated Data: Failed to connect or data structure is incorrect. ")
    df_sales = get_simulated_data()
    # If simulated data is also empty, stop execution
    if df_sales.empty:
        st.error("Could not load any data. Please check the API or the simulation.")
        st.stop()


# 2. Sidebar with Accordion (st.expander) and Filters
st.sidebar.title("🛠️ Analysis Filters")

with st.sidebar.expander("Data Filters (Accordion)", expanded=True):
    # Filter 1: Month
    try:
        available_months = sorted(df_sales['month_name'].unique(), key=lambda m: datetime.strptime(m, '%B'))
    except: # Fallback in case month names are not standard English
         available_months = sorted(df_sales['month_name'].unique())
         
    selected_month = st.selectbox(
        "Select Month", 
        options=available_months, 
        index=len(available_months) - 1 if available_months else 0 # Select the latest month
    )

    # Filter 2: Product Category
    available_categories = sorted(df_sales['category'].unique())
    selected_categories = st.multiselect(
        "Select Categories",
        options=available_categories,
        default=available_categories 
    )

# 3. Apply Filters
df_filtered = df_sales[
    (df_sales['month_name'] == selected_month) & 
    (df_sales['category'].isin(selected_categories))
].copy() 


# 4. HOME PAGE LAYOUT
st.title("📈 Product Revenue Dashboard")
st.markdown(f"**Data based on Spring Boot API connection** | Analysis Month: **{selected_month}**")

st.divider() # Divider line


# --- 5. DYNAMIC VISUALIZATIONS AND KPIS ---

if df_filtered.empty:
    st.warning("No data to display with the applied filters. Adjust your selections.")
else:
    # KPI 1: Total Revenue
    total_revenue = df_filtered['revenue'].sum()
    st.metric(
        label="Total Monthly Revenue", 
        value=f"${total_revenue:,.2f}",
        delta="Real API Data"
    )

    # Container for Analysis Charts (using st.columns)
    col1, col2 = st.columns(2)

    # CHART 1: Revenue by Category 
    with col1:
        st.subheader("Total Revenue by Category")
        
        # Group and prepare data for the chart
        df_comparison = df_filtered.groupby('category')['revenue'].sum().reset_index()
        
        # Create Plotly Bar Chart
        fig_bar = px.bar(
            df_comparison,
            x='category',
            y='revenue',
            color='category', # Color by category to distinguish them
            title='Revenue Comparison',
            labels={'revenue': 'Revenue ($)', 'category': 'Category'},
            template='streamlit'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # CHART 2: Daily Revenue Trend
    with col2:
        st.subheader("Daily Revenue Trend")
        
        df_trend = df_filtered.groupby('date')['revenue'].sum().reset_index()
        
        fig_line = px.line(
            df_trend,
            x='date',
            y='revenue',
            title='Cumulative Daily Revenue',
            labels={'revenue': 'Revenue ($)', 'date': 'Date'},
            template='streamlit'
        )
        st.plotly_chart(fig_line, use_container_width=True)


    st.divider()

    # --- 6. DYNAMIC TEXT REPORT (Highest Revenue Analysis) ---
    st.subheader("🔎 Monthly Analysis Conclusion")

    # Logic to determine the highest revenue 
    if not df_comparison.empty:
        max_revenue = df_comparison['revenue'].max()
        max_category = df_comparison[df_comparison['revenue'] == max_revenue]['category'].iloc[0]
        
        st.success(
            f"**Key Insight!** In **{selected_month}**, the category with the highest reported revenue was **{max_category}** "
            f"with a total of **${max_revenue:,.2f}**. "
            "This indicates a significant business focus in this area."
        )

        # Optional: Show the complete table
        with st.expander("View Filtered Raw Data"):
            st.dataframe(df_filtered, use_container_width=True)