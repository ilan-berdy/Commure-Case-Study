import streamlit as st
import pandas as pd
import plotly.express as px
from simple_rcm_model import SimpleRCMModel

# Page config
st.set_page_config(
    page_title="Simple RCM Capacity Planning",
    layout="wide"
)

# Title and intro
st.title("Simple RCM Capacity Planning Dashboard")
st.markdown("""
This dashboard shows the capacity planning for a manual Revenue Cycle Management rollout 
across 100 healthcare practices over a 3-month onboarding period. This is a simplified version
that focuses on core operational requirements.
""")

# Initialize model
model = SimpleRCMModel()

# Generate report
report = model.generate_report()

# KPI Summary
st.header("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Gross Margin",
        f"{report['Gross Margin %'].iloc[-1]:.1f}%",
        f"{report['Gross Margin %'].iloc[-1] - report['Gross Margin %'].iloc[0]:.1f}%"
    )

with col2:
    st.metric(
        "Monthly Revenue",
        f"${report['Monthly Revenue'].iloc[-1]/1000:.0f}K",
        f"${(report['Monthly Revenue'].iloc[-1] - report['Monthly Revenue'].iloc[0])/1000:.0f}K"
    )

with col3:
    st.metric(
        "Active Accounts",
        f"{report['Active Accounts'].iloc[-1]:.0f}",
        f"{report['Active Accounts'].iloc[-1] - report['Active Accounts'].iloc[0]:.0f}"
    )

with col4:
    total_staff = report['Analyst Count'].iloc[-1] + report['Manager Count'].iloc[-1]
    initial_staff = report['Analyst Count'].iloc[0] + report['Manager Count'].iloc[0]
    st.metric(
        "Total Staff",
        f"{total_staff:.0f}",
        f"{total_staff - initial_staff:.0f}"
    )

# Main metrics
st.header("Monthly Metrics")

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Staffing & Claims", "Financial Metrics", "Raw Data"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Staffing growth chart
        fig_staff = px.line(
            report,
            x='Month',
            y=['Analyst Count', 'Manager Count'],
            markers=True,
            title='Staffing Growth'
        )
        fig_staff.update_layout(
            yaxis_title="Headcount",
            template="plotly_white"
        )
        st.plotly_chart(fig_staff, use_container_width=True)
    
    with col2:
        # Claims volume chart
        fig_claims = px.line(
            report,
            x='Month',
            y='Monthly Claims',
            markers=True,
            title='Monthly Claims Volume'
        )
        fig_claims.update_layout(
            yaxis_title="Number of Claims",
            template="plotly_white"
        )
        st.plotly_chart(fig_claims, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue and costs chart
        fig_finance = px.bar(
            report,
            x='Month',
            y=['Monthly Revenue', 'Labor Cost'],
            barmode='group',
            title='Revenue vs. Costs'
        )
        fig_finance.update_layout(
            yaxis_title="USD",
            template="plotly_white"
        )
        st.plotly_chart(fig_finance, use_container_width=True)
    
    with col2:
        # Gross margin chart
        fig_margin = px.line(
            report,
            x='Month',
            y='Gross Margin %',
            markers=True,
            title='Gross Margin Trend'
        )
        fig_margin.update_layout(
            yaxis_title="Percentage",
            template="plotly_white"
        )
        st.plotly_chart(fig_margin, use_container_width=True)

with tab3:
    # Display raw data
    st.dataframe(
        report.style.format({
            'Monthly Revenue': '${:,.0f}',
            'Labor Cost': '${:,.0f}',
            'Gross Margin %': '{:.1f}%',
            'Monthly Claims': '{:,.0f}',
            'Daily Claims': '{:.1f}',
            'Claims per Analyst per Day': '{:.1f}',
            'Total Time per Claim (min)': '{:.1f}',
            'Analyst Count': '{:.0f}',
            'Manager Count': '{:.0f}'
        })
    )

# Model assumptions
with st.expander("Model Assumptions"):
    st.markdown("""
    ### Core Parameters
    - Total Accounts: 100
    - Total Claims Value: $200M
    - Average Claim Value: $200
    - Revenue Percentage: 5%
    - Target Margin: 60%
    - Target Approval Rate: 90%
    
    ### Process Parameters
    - Time per Step: 2-5 minutes
    - Account Onboarding:
        - Month 1: 10 accounts
        - Month 2: 30 accounts
        - Month 3: 60 accounts
    
    ### Labor Costs (Fully Loaded)
    - Analyst Base Salary: $500/month
    - Fully Loaded Cost: $750/month (1.5× base)
    - Manager Cost: $1,125/month (1.5× analyst cost)
    - Manager Ratio: 1:12 analysts
    """) 