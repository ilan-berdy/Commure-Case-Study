import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from simple_rcm_model import SimpleRCMModel

# Set page config
st.set_page_config(
    page_title="RCM Capacity Planning Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize model
model = SimpleRCMModel()

# Title and description
st.title("RCM Capacity Planning Dashboard")
st.markdown("""
This dashboard shows the capacity planning model for a Revenue Cycle Management (RCM) service
that will be rolled out across 100 healthcare practices over three months.
""")

# Generate data
report = model.generate_report()

# Display key metrics
st.header("Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Gross Margin",
        f"{report['Gross Margin %'].iloc[-1]:.1f}%",
        f"{report['Gross Margin %'].iloc[-1] - report['Gross Margin %'].iloc[0]:.1f}%"
    )

with col2:
    st.metric(
        "Monthly Revenue",
        f"${report['Monthly Revenue'].iloc[-1]:,.0f}",
        f"${report['Monthly Revenue'].iloc[-1] - report['Monthly Revenue'].iloc[0]:,.0f}"
    )

with col3:
    st.metric(
        "Active Accounts",
        f"{report['Active Accounts'].iloc[-1]:.0f}",
        f"{report['Active Accounts'].iloc[-1] - report['Active Accounts'].iloc[0]:.0f}"
    )

with col4:
    st.metric(
        "Total Staff",
        f"{report['Total Analyst Count'].iloc[-1] + report['Manager Count'].iloc[-1]:.0f}",
        f"{(report['Total Analyst Count'].iloc[-1] + report['Manager Count'].iloc[-1]) - (report['Total Analyst Count'].iloc[0] + report['Manager Count'].iloc[0]):.0f}"
    )

with col5:
    st.metric(
        "Approval Rate",
        f"{report['Approval Rate'].iloc[-1]:.1f}%",
        f"{report['Approval Rate'].iloc[-1] - report['Approval Rate'].iloc[0]:.1f}%"
    )

# SLA Compliance Section
st.header("SLA Compliance")
sla_col1, sla_col2 = st.columns(2)

with sla_col1:
    # Submission SLA
    submission_sla = "✅ Met" if report['Submission SLA Met'].iloc[-1] else "❌ Not Met"
    st.metric(
        "Submission SLA (5 days)",
        submission_sla,
        f"Utilization: {report['Submission Utilization %'].iloc[-1]:.1f}%"
    )

with sla_col2:
    # Denial SLA
    denial_sla = "✅ Met" if report['Denial SLA Met'].iloc[-1] else "❌ Not Met"
    st.metric(
        "Denial Work SLA (3 days)",
        denial_sla,
        f"Utilization: {report['Denial Utilization %'].iloc[-1]:.1f}%"
    )

# Staffing Section
st.header("Staffing Analysis")
staff_col1, staff_col2 = st.columns(2)

with staff_col1:
    # Staffing breakdown
    fig_staff = go.Figure()
    fig_staff.add_trace(go.Bar(
        x=report['Month'],
        y=report['Submission Analysts'],
        name='Submission Analysts',
        marker_color='rgb(55, 83, 109)'
    ))
    fig_staff.add_trace(go.Bar(
        x=report['Month'],
        y=report['Denial Analysts'],
        name='Denial Analysts',
        marker_color='rgb(26, 118, 255)'
    ))
    fig_staff.add_trace(go.Bar(
        x=report['Month'],
        y=report['Manager Count'],
        name='Managers',
        marker_color='rgb(255, 65, 54)'
    ))
    fig_staff.update_layout(
        title='Staffing Growth by Role',
        xaxis_title='Month',
        yaxis_title='Headcount',
        barmode='stack'
    )
    st.plotly_chart(fig_staff, use_container_width=True)

with staff_col2:
    # Revenue vs Costs
    fig_revenue = go.Figure()
    fig_revenue.add_trace(go.Bar(
        x=report['Month'],
        y=report['Monthly Revenue'],
        name='Revenue',
        marker_color='rgb(55, 83, 109)'
    ))
    fig_revenue.add_trace(go.Bar(
        x=report['Month'],
        y=report['Labor Cost'],
        name='Labor Cost',
        marker_color='rgb(26, 118, 255)'
    ))
    fig_revenue.update_layout(
        title='Revenue vs Labor Costs',
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        barmode='group'
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

# Denial Work Ramp-up Section
st.header("Denial Work Ramp-up Analysis")
denial_col1, denial_col2 = st.columns(2)

with denial_col1:
    # Weekly denial metrics for the last month
    last_month_metrics = report['Weekly Denial Metrics'].iloc[-1]
    weeks = list(range(1, 13))
    denial_claims = [last_month_metrics[f'Week_{w}']['Denial_Claims'] for w in weeks]
    denial_capacity = [last_month_metrics[f'Week_{w}']['Capacity'] for w in weeks]
    denial_utilization = [last_month_metrics[f'Week_{w}']['Utilization'] for w in weeks]
    
    fig_denial = go.Figure()
    fig_denial.add_trace(go.Scatter(
        x=weeks,
        y=denial_claims,
        name='Denial Claims',
        line=dict(color='rgb(55, 83, 109)')
    ))
    fig_denial.add_trace(go.Scatter(
        x=weeks,
        y=denial_capacity,
        name='Capacity',
        line=dict(color='rgb(26, 118, 255)')
    ))
    fig_denial.update_layout(
        title='Weekly Denial Work Volume vs Capacity',
        xaxis_title='Week',
        yaxis_title='Claims/Capacity'
    )
    st.plotly_chart(fig_denial, use_container_width=True)

with denial_col2:
    # Submission utilization including denial analysts
    submission_utilization = [last_month_metrics[f'Week_{w}']['Submission_Utilization'] for w in weeks]
    effective_capacity = [last_month_metrics[f'Week_{w}']['Effective_Submission_Capacity'] for w in weeks]
    
    fig_utilization = go.Figure()
    fig_utilization.add_trace(go.Scatter(
        x=weeks,
        y=submission_utilization,
        name='Submission Utilization',
        line=dict(color='rgb(255, 65, 54)')
    ))
    fig_utilization.add_trace(go.Scatter(
        x=weeks,
        y=denial_utilization,
        name='Denial Utilization',
        line=dict(color='rgb(26, 118, 255)')
    ))
    fig_utilization.update_layout(
        title='Weekly Utilization Including Denial Analysts on Submissions',
        xaxis_title='Week',
        yaxis_title='Utilization %',
        yaxis_range=[0, 100]
    )
    st.plotly_chart(fig_utilization, use_container_width=True)

# Add explanation of denial analyst allocation
st.markdown("""
### Denial Analyst Allocation Strategy
- **Weeks 1-2**: All denial analysts work on submissions (100% submission capacity)
- **Week 3**: 75% submission, 25% denial work
- **Week 4**: 50% submission, 50% denial work
- **Week 5**: 25% submission, 75% denial work
- **Week 6+**: Full denial work (100% denial capacity)

This strategy optimizes resource utilization by having denial analysts contribute to submission work during the initial weeks when there are no denials to process.
""")

# Detailed Metrics
st.header("Detailed Metrics")
st.dataframe(
    report[[
        'Month',
        'Active Accounts',
        'Monthly Claims',
        'Approved Claims',
        'Denied Claims',
        'Approval Rate',
        'Total Analyst Count',
        'Submission Analysts',
        'Denial Analysts',
        'Manager Count',
        'Labor Cost',
        'Monthly Revenue',
        'Gross Margin %',
        'Submission Utilization %',
        'Denial Utilization %'
    ]].style.format({
        'Monthly Claims': '{:,.0f}',
        'Approved Claims': '{:,.0f}',
        'Denied Claims': '{:,.0f}',
        'Approval Rate': '{:.1f}%',
        'Total Analyst Count': '{:.0f}',
        'Submission Analysts': '{:.0f}',
        'Denial Analysts': '{:.0f}',
        'Manager Count': '{:.0f}',
        'Labor Cost': '${:,.0f}',
        'Monthly Revenue': '${:,.0f}',
        'Gross Margin %': '{:.1f}%',
        'Submission Utilization %': '{:.1f}%',
        'Denial Utilization %': '{:.1f}%'
    })
)

# Model Assumptions
st.header("Model Assumptions")
assumptions = {
    "Claims per Practice": f"{model.CLAIMS_PER_PRACTICE:,} per year",
    "Average Claim Value": f"${model.AVG_CLAIM_VALUE}",
    "Revenue Percentage": f"{model.REVENUE_PERCENTAGE*100}%",
    "Target Approval Rate": f"{model.TARGET_APPROVAL_RATE*100}%",
    "Submission SLA": f"{model.SUBMISSION_SLA} days",
    "Denial Work SLA": f"{model.DENIAL_WORK_SLA} days",
    "Analyst Allocation": f"Submission: {model.SUBMISSION_ALLOCATION*100}%, Denial: {model.DENIAL_ALLOCATION*100}%",
    "Working Days per Month": f"{model.DAYS_PER_MONTH}",
    "Hours per Day": f"{model.HOURS_PER_DAY}"
}

for key, value in assumptions.items():
    st.markdown(f"- **{key}**: {value}")

# Denial Ramp-up Profile
st.header("Denial Work Ramp-up Profile")
ramp_up_data = pd.DataFrame([
    {"Week": week, "Capacity": factor * 100}
    for week, factor in model.DENIAL_RAMP_UP.items()
])

fig_ramp_up = px.line(
    ramp_up_data,
    x='Week',
    y='Capacity',
    markers=True,
    title='Denial Work Capacity Ramp-up'
)
fig_ramp_up.update_layout(
    yaxis_title='Capacity %',
    yaxis_range=[0, 100]
)
st.plotly_chart(fig_ramp_up, use_container_width=True) 