import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page setup
st.set_page_config(page_title="User Behavior & Revenue Dashboard", layout="wide")
st.markdown("## User Behavior & Revenue Dashboard")
st.caption("Interactive analysis of user engagement, monetization, and churn patterns")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df.columns = df.columns.str.strip().str.replace(" ", "_")
    df['Signup_Date'] = pd.to_datetime(df['Signup_Date'], dayfirst=True, errors='coerce')
    df['Last_Login'] = pd.to_datetime(df['Last_Login'], dayfirst=True, errors='coerce')
    df['Login_Date'] = df['Last_Login'].dt.date
    df['Week'] = df['Last_Login'].dt.strftime('%Y-%U')
    df['Month'] = df['Last_Login'].dt.to_period('M').astype(str)
    df['Days_Since_Last_Login'] = (pd.to_datetime("today") - df['Last_Login']).dt.days
    return df

df = load_data()
if df.empty:
    st.stop()

st.success(f"Loaded {df.shape[0]} user records")

# Sidebar filters
with st.sidebar:
    st.header("Filter Data")
    selected_country = st.multiselect("Country", df["Country"].dropna().unique(), default=df["Country"].dropna().unique())
    selected_device = st.multiselect("Device Type", df["Device_Type"].dropna().unique(), default=df["Device_Type"].dropna().unique())

filtered_df = df[(df["Country"].isin(selected_country)) & (df["Device_Type"].isin(selected_device))]
st.info(f"Showing {filtered_df.shape[0]} records based on current filters")

st.divider()

# Key Metrics
st.subheader("Key Metrics Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Users", f"{filtered_df['User_ID'].nunique()}")
col2.metric("Total Revenue", f"${filtered_df['Total_Revenue_USD'].sum():,.2f}")
col3.metric("Avg. Session Duration", f"{filtered_df['Avg_Session_Duration_Min'].mean():.2f} min")

st.divider()

# Engagement Trends
st.subheader("Engagement Trends")

dau = filtered_df.groupby('Login_Date')['User_ID'].nunique().reset_index(name='DAU')
wau = filtered_df.groupby('Week')['User_ID'].nunique().reset_index(name='WAU')
monthly_active_users = df.groupby('Month')['User_ID'].nunique().reset_index(name='MAU')

tab1, tab2, tab3 = st.tabs(["Daily", "Weekly", "Monthly"])
with tab1:
    fig_dau = px.line(dau, x='Login_Date', y='DAU', title="Daily Active Users", template='plotly_white')
    st.plotly_chart(fig_dau, use_container_width=True)

with tab2:
    fig_wau = px.line(wau, x='Week', y='WAU', title="Weekly Active Users", template='plotly_white')
    st.plotly_chart(fig_wau, use_container_width=True)

with tab3:
    try:
        fig_mau = px.line(monthly_active_users, x='Month', y='MAU', title="Monthly Active Users", template='plotly_white', markers=True)
        st.plotly_chart(fig_mau, use_container_width=True)
    except:
        st.line_chart(monthly_active_users.set_index('Month'))

st.divider()

# Revenue Trends Over Time
st.subheader("Cumulative Revenue Trend (by Signup Date)")

revenue_by_signup = df.dropna(subset=['Signup_Date']).copy()
revenue_by_signup['Signup_Date'] = pd.to_datetime(revenue_by_signup['Signup_Date'], errors='coerce')
daily_revenue = revenue_by_signup.groupby('Signup_Date')['Total_Revenue_USD'].sum().sort_index().cumsum().reset_index()
daily_revenue.columns = ['Date', 'Cumulative_Revenue']

try:
    fig_rev = px.line(
        daily_revenue,
        x='Date',
        y='Cumulative_Revenue',
        title="Cumulative Revenue Over Time",
        template='plotly_white',
        labels={'Cumulative_Revenue': 'USD'}
    )
    st.plotly_chart(fig_rev, use_container_width=True)
except:
    st.line_chart(daily_revenue.set_index('Date'))

st.divider()

# Revenue Breakdown
st.subheader("Revenue Breakdown by Segment")
col1, col2, col3 = st.columns(3)

with col1:
    rev_device = filtered_df.groupby('Device_Type')['Total_Revenue_USD'].sum().reset_index()
    st.plotly_chart(px.bar(rev_device, x='Device_Type', y='Total_Revenue_USD', title="By Device Type", template='plotly_white'), use_container_width=True)

with col2:
    rev_tier = filtered_df.groupby('Subscription_Tier')['Total_Revenue_USD'].sum().reset_index()
    st.plotly_chart(px.bar(rev_tier, x='Subscription_Tier', y='Total_Revenue_USD', title="By User Segment", template='plotly_white'), use_container_width=True)

with col3:
    rev_mode = filtered_df.groupby('Preferred_Game_Mode')['Total_Revenue_USD'].sum().reset_index()
    st.plotly_chart(px.bar(rev_mode, x='Preferred_Game_Mode', y='Total_Revenue_USD', title="By Game Mode", template='plotly_white'), use_container_width=True)

st.divider()

# High-Value Users
st.subheader("High-Value Users")
top_10 = filtered_df.sort_values(by='Total_Revenue_USD', ascending=False).head(10)
st.dataframe(
    top_10[['Username', 'Total_Revenue_USD', 'Total_Play_Sessions', 'Preferred_Game_Mode']]
)

# Footer
st.divider()
st.caption("Built by Sahil")
