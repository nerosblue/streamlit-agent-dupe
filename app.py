import streamlit as st
import pandas as pd
import altair as alt

# --- Page Configuration ---
st.set_page_config(
    page_title="UK House Price Dashboard",
    layout="wide"
)

# --- Data Loading ---
# This function loads all 7 CSVs and merges them.
# @st.cache_data ensures this only runs once.
@st.cache_data
def load_all_data():
    # Define file names and the keys to merge on
    files = [
        "Average-prices-Property-Type-2025-06.csv",
        "Cash-mortgage-sales-2025-06.csv",
        "First-Time-Buyer-Former-Owner-Occupied-2025-06.csv",
        "Indices-2025-06.csv",
        "Indices-seasonally-adjusted-2025-06.csv",
        "New-and-Old-2025-06.csv",
        "Sales-2025-06.csv"
    ]
    merge_keys = ['Date', 'Region_Name', 'Area_Code']
    
    # Load the first file as the base DataFrame
    try:
        df_merged = pd.read_csv(files[0])
        df_merged['Date'] = pd.to_datetime(df_merged['Date'])
    except FileNotFoundError:
        st.error(f"Error: File '{files[0]}' not found.")
        st.stop()

    # Loop through the rest of the files and merge them
    for file in files[1:]:
        try:
            df_temp = pd.read_csv(file)
            df_temp['Date'] = pd.to_datetime(df_temp['Date'])
            
            # Use 'outer' merge to keep all data from all files
            df_merged = pd.merge(df_merged, df_temp, on=merge_keys, how='outer', suffixes=('', f'_{file.split("-")[0]}'))
        except FileNotFoundError:
            st.error(f"Error: File '{file}' not found. Skipping this file.")
        except Exception as e:
            st.error(f"Error merging {file}: {e}")
            
    return df_merged

# Load the data
df = load_all_data()

# --- Sidebar ---
st.sidebar.title("Navigation & Filters 🧭")

# Create a list of regions, with 'United Kingdom' at the top
all_regions = sorted(df['Region_Name'].unique())
if "United Kingdom" in all_regions:
    all_regions.remove("United Kingdom")
    all_regions = ["United Kingdom"] + all_regions

selected_region = st.sidebar.selectbox(
    "Select a Region:",
    options=all_regions
)

# Filter the main DataFrame based on the selected region
df_region = df[df['Region_Name'] == selected_region].copy()

# Sidebar navigation for different pages
page = st.sidebar.radio(
    "Select an Analysis:",
    [
        "Data Overview",
        "Property Type Comparison",
        "Buyer Type Comparison",
        "New vs. Existing Builds",
        "Sales Volume Analysis"
    ]
)

# --- Main App Title ---
st.title(f"UK House Price Analysis 🏠")
st.subheader(f"Showing data for: {selected_region}")


# --- Page Routing ---

if page == "Data Overview":
    st.header("Merged Data Overview")
    st.write(f"The full dataset has {df.shape[0]} rows and {df.shape[1]} columns.")
    st.dataframe(df.head())
    
    st.subheader("Data Description (for selected region)")
    st.write(df_region.describe())

elif page == "Property Type Comparison":
    st.header("Property Type Comparison")
    st.write("Average prices for different property types over time.")

    # Columns to plot
    price_cols = ['Detached_Average_Price', 'Semi_Detached_Average_Price', 'Terraced_Average_Price', 'Flat_Average_Price']
    
    # "Melt" the DataFrame to make it long-form, which is what Altair likes
    df_melted = df_region.melt(
        id_vars=['Date'], 
        value_vars=price_cols, 
        var_name='Property Type', 
        value_name='Average Price'
    )
    
    # Create the chart
    chart = alt.Chart(df_melted).mark_line(point=True).encode(
        x=alt.X('Date', title='Date'),
        y=alt.Y('Average Price', title='Average Price (GBP)'),
        color='Property Type',
        tooltip=['Date', 'Property Type', alt.Tooltip('Average Price', format=',.0f')]
    ).properties(
        title="Average Price by Property Type"
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)

elif page == "Buyer Type Comparison":
    st.header("Buyer Type Comparison")
    
    st.subheader("First-Time Buyer vs. Former Owner")
    
    # Melt for First-Time vs. Former Owner
    df_melted_1 = df_region.melt(
        id_vars=['Date'], 
        value_vars=['First_Time_Buyer_Average_Price', 'Former_Owner_Occupier_Average_Price'], 
        var_name='Buyer Type', 
        value_name='Average Price'
    )
    
    chart_1 = alt.Chart(df_melted_1).mark_line().encode(
        x='Date',
        y=alt.Y('Average Price', title='Average Price (GBP)'),
        color='Buyer Type',
        tooltip=['Date', 'Buyer Type', alt.Tooltip('Average Price', format=',.0f')]
    ).properties(
        title="First-Time Buyer vs. Former Owner Prices"
    ).interactive()
    
    st.altair_chart(chart_1, use_container_width=True)

    st.subheader("Cash vs. Mortgage Buyers")
    
    # Melt for Cash vs. Mortgage
    df_melted_2 = df_region.melt(
        id_vars=['Date'], 
        value_vars=['Cash_Average_Price', 'Mortgage_Average_Price'], 
        var_name='Purchase Type', 
        value_name='Average Price'
    )
    
    chart_2 = alt.Chart(df_melted_2).mark_line().encode(
        x='Date',
        y=alt.Y('Average Price', title='Average Price (GBP)'),
        color='Purchase Type',
        tooltip=['Date', 'Purchase Type', alt.Tooltip('Average Price', format=',.0f')]
    ).properties(
        title="Cash vs. Mortgage Buyer Prices"
    ).interactive()
    
    st.altair_chart(chart_2, use_container_width=True)

elif page == "New vs. Existing Builds":
    st.header("New vs. Existing Builds")
    st.write("Average prices for new-build vs. existing properties.")

    # Melt for New vs. Existing
    df_melted = df_region.melt(
        id_vars=['Date'], 
        value_vars=['New_Build_Average_Price', 'Existing_Property_Average_Price'], 
        var_name='Build Type', 
        value_name='Average Price'
    )
    
    chart = alt.Chart(df_melted).mark_line().encode(
        x='Date',
        y=alt.Y('Average Price', title='Average Price (GBP)'),
        color='Build Type',
        tooltip=['Date', 'Build Type', alt.Tooltip('Average Price', format=',.0f')]
    ).properties(
        title="New Build vs. Existing Property Prices"
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)
    
elif page == "Sales Volume Analysis":
    st.header("Sales Volume Analysis")
    
    st.subheader("Total Sales Volume Over Time")
    
    # Simple line chart for total sales volume
    chart_total = alt.Chart(df_region).mark_line().encode(
        x=alt.X('Date', title='Date'),
        y=alt.Y('Sales_Volume', title='Number of Sales'),
        tooltip=['Date', alt.Tooltip('Sales_Volume', format=',.0f')]
    ).properties(
        title="Total Sales Volume"
    ).interactive()
    
    st.altair_chart(chart_total, use_container_width=True)
    
    st.subheader("Sales Volume by Type")
    
    # Melt for different sales volume types
    sales_cols = ['Cash_Sales_Volume', 'Mortgage_Sales_Volume', 'New_Build_Sales_Volume', 'Existing_Property_Sales_Volume']
    df_melted_sales = df_region.melt(
        id_vars=['Date'], 
        value_vars=sales_cols, 
        var_name='Sales Type', 
        value_name='Number of Sales'
    )
    
    chart_sales = alt.Chart(df_melted_sales).mark_line(point=True).encode(
        x=alt.X('Date', title='Date'),
        y=alt.Y('Number of Sales', title='Number of Sales'),
        color='Sales Type',
        tooltip=['Date', 'Sales Type', alt.Tooltip('Number of Sales', format=',.0f')]
    ).properties(
        title="Sales Volume by Type"
    ).interactive()
    
    st.altair_chart(chart_sales, use_container_width=True)
