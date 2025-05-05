import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from simple_rcm_model import SimpleRCMModel
from simple_rcm_optimizer import SimpleRCMOptimizer
import numpy as np

# Set page config
st.set_page_config(
    page_title="RCM Optimization Plan",
    page_icon="📊",
    layout="wide"
)

class RCMDashboard:
    def __init__(self):
        self.model = SimpleRCMModel()
        self.optimizer = SimpleRCMOptimizer(self.model)
        self.colors = {
            'submission_analysts': '#2ecc71',
            'denial_analysts': '#e74c3c',
            'managers': '#3498db',
            'implementation_staff': '#9b59b6',
            'customer_success': '#f1c40f',
            'revenue': '#27ae60',
            'labor': '#c0392b',
            'overhead': '#d35400',
            'margin': '#2980b9'
        }
        
        # Run optimization
        self.solution = self.optimizer.optimize()
        
        # Calculate key metrics
        self.calculate_metrics()
    
    def calculate_metrics(self):
        """Calculate all metrics needed for the dashboard"""
        # Staffing calculations
        self.submission_analysts = self.solution['submission_analysts']
        self.denial_analysts = self.solution['denial_analysts']
        total_analysts = self.submission_analysts + self.denial_analysts
        self.managers = np.ceil(total_analysts / self.model.ANALYSTS_PER_MANAGER)
        self.implementation_staff = self.solution['implementation_staff']
        
        # Account ramp-up
        self.total_accounts = 100
        self.ramp_up_schedule = [0.1, 0.3, 0.6, 1.0]  # 10/30/60/100 schedule
        self.monthly_accounts = [self.total_accounts * rate for rate in self.ramp_up_schedule]
        
        # CS staff based on accounts
        self.cs_staff = [np.ceil(accounts / self.model.ACCOUNTS_PER_CUSTOMER_SUCCESS) 
                        for accounts in self.monthly_accounts]
        
        # Financial calculations
        self.monthly_metrics = []
        for month in range(4):
            metrics = self.model.calculate_monthly_metrics(month)
            
            # Calculate overhead costs
            overhead = (
                metrics.get('Software Cost', 0) +
                metrics.get('Office Cost', 0) +
                metrics.get('Training Cost', 0) +
                metrics.get('Infrastructure Cost', 0) +
                metrics.get('Compliance Cost', 0) +
                metrics.get('QA Cost', 0) +
                metrics.get('Setup Cost', 0)  # Add setup cost to overhead
            )
            
            self.monthly_metrics.append({
                'Month': month,
                'Revenue': metrics['Monthly Revenue'],
                'Labor Cost': metrics['Total Labor Cost'],
                'Overhead': overhead,
                'Net Margin': metrics['Monthly Revenue'] - metrics['Total Labor Cost'] - overhead,
                'Accounts': self.monthly_accounts[month],
                'Submission SLA Met': metrics['Submission SLA Met'],
                'Denial SLA Met': metrics['Denial SLA Met'],
                'Submission Utilization': metrics['Submission Utilization %'],
                'Denial Utilization': metrics['Denial Utilization %']
            })
    
    def generate_staffing_summary(self):
        """Generate staffing summary table and chart"""
        # Create staffing table
        staffing_data = pd.DataFrame({
            'Role': ['Submission Analysts', 'Denial Analysts', 'Managers', 
                    'Implementation Staff', 'Customer Success'],
            'Month 0': [self.submission_analysts, self.denial_analysts, self.managers,
                       self.implementation_staff, self.cs_staff[0]],
            'Month 1': [self.submission_analysts, self.denial_analysts, self.managers,
                       self.implementation_staff, self.cs_staff[1]],
            'Month 2': [self.submission_analysts * 2, self.denial_analysts * 2, 
                       self.managers * 2, self.implementation_staff * 2, self.cs_staff[2]],
            'Month 3': [self.submission_analysts * 3, self.denial_analysts * 3,
                       self.managers * 3, self.implementation_staff * 3, self.cs_staff[3]]
        })
        
        # Create stacked bar chart
        fig = go.Figure()
        months = ['Month 0', 'Month 1', 'Month 2', 'Month 3']
        roles = ['Submission Analysts', 'Denial Analysts', 'Managers', 
                'Implementation Staff', 'Customer Success']
        
        # Color mapping
        role_colors = {
            'Submission Analysts': self.colors['submission_analysts'],
            'Denial Analysts': self.colors['denial_analysts'],
            'Managers': self.colors['managers'],
            'Implementation Staff': self.colors['implementation_staff'],
            'Customer Success': self.colors['customer_success']
        }
        
        for role in roles:
            fig.add_trace(go.Bar(
                name=role,
                x=months,
                y=staffing_data[months].loc[staffing_data['Role'] == role].values[0],
                marker_color=role_colors[role]
            ))
        
        fig.update_layout(
            title='Staffing Levels by Role',
            barmode='stack',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return staffing_data, fig
    
    def generate_financial_summary(self):
        """Generate financial summary table and waterfall chart"""
        # Create financial metrics table
        metrics_df = pd.DataFrame(self.monthly_metrics)
        financial_summary = pd.DataFrame({
            'Metric': ['Total Revenue', 'Labor Cost', 'Overhead', 'Net Margin', 'Gross Margin %'],
            'Month 0': [
                f"${metrics_df['Revenue'].iloc[0]:,.0f}",
                f"${metrics_df['Labor Cost'].iloc[0]:,.0f}",
                f"${metrics_df['Overhead'].iloc[0]:,.0f}",
                f"${metrics_df['Net Margin'].iloc[0]:,.0f}",
                f"{(metrics_df['Net Margin'].iloc[0] / metrics_df['Revenue'].iloc[0] * 100):.1f}%"
            ],
            'Month 1': [
                f"${metrics_df['Revenue'].iloc[1]:,.0f}",
                f"${metrics_df['Labor Cost'].iloc[1]:,.0f}",
                f"${metrics_df['Overhead'].iloc[1]:,.0f}",
                f"${metrics_df['Net Margin'].iloc[1]:,.0f}",
                f"{(metrics_df['Net Margin'].iloc[1] / metrics_df['Revenue'].iloc[1] * 100):.1f}%"
            ],
            'Month 2': [
                f"${metrics_df['Revenue'].iloc[2]:,.0f}",
                f"${metrics_df['Labor Cost'].iloc[2]:,.0f}",
                f"${metrics_df['Overhead'].iloc[2]:,.0f}",
                f"${metrics_df['Net Margin'].iloc[2]:,.0f}",
                f"{(metrics_df['Net Margin'].iloc[2] / metrics_df['Revenue'].iloc[2] * 100):.1f}%"
            ],
            'Month 3': [
                f"${metrics_df['Revenue'].iloc[3]:,.0f}",
                f"${metrics_df['Labor Cost'].iloc[3]:,.0f}",
                f"${metrics_df['Overhead'].iloc[3]:,.0f}",
                f"${metrics_df['Net Margin'].iloc[3]:,.0f}",
                f"{(metrics_df['Net Margin'].iloc[3] / metrics_df['Revenue'].iloc[3] * 100):.1f}%"
            ]
        })
        
        # Create waterfall chart
        fig = go.Figure()
        
        # Add revenue bars (positive)
        fig.add_trace(go.Bar(
            name='Revenue',
            x=['Month ' + str(i) for i in range(4)],
            y=metrics_df['Revenue'],
            marker_color=self.colors['revenue']
        ))
        
        # Add labor cost bars (negative)
        fig.add_trace(go.Bar(
            name='Labor Cost',
            x=['Month ' + str(i) for i in range(4)],
            y=-metrics_df['Labor Cost'],
            marker_color=self.colors['labor']
        ))
        
        # Add overhead bars (negative, stacked on labor cost)
        fig.add_trace(go.Bar(
            name='Overhead',
            x=['Month ' + str(i) for i in range(4)],
            y=-metrics_df['Overhead'],
            marker_color=self.colors['overhead'],
            base=-metrics_df['Labor Cost']  # Stack on top of labor cost
        ))
        
        # Add net margin line
        fig.add_trace(go.Scatter(
            name='Net Margin',
            x=['Month ' + str(i) for i in range(4)],
            y=metrics_df['Net Margin'],
            mode='lines+markers',
            line=dict(color=self.colors['margin'], width=2)
        ))
        
        # Update layout
        fig.update_layout(
            title='Financial Performance',
            barmode='relative',  # Changed back to 'relative' for stacking
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis_title='Amount ($)',
            bargap=0.15,  # Add some space between bar groups
            bargroupgap=0.1  # Add space between bars in the same group
        )
        
        # Add a horizontal line at y=0
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        return financial_summary, fig
    
    def generate_operational_summary(self):
        """Generate operational metrics summary"""
        metrics_df = pd.DataFrame(self.monthly_metrics)
        
        # Create operational metrics table
        operational_summary = pd.DataFrame({
            'Metric': ['Active Accounts', 'Submission SLA', 'Denial SLA', 
                      'Submission Utilization', 'Denial Utilization'],
            'Month 0': [
                f"{metrics_df['Accounts'].iloc[0]:.0f}",
                "Met" if metrics_df['Submission SLA Met'].iloc[0] else "Not Met",
                "Met" if metrics_df['Denial SLA Met'].iloc[0] else "Not Met",
                f"{metrics_df['Submission Utilization'].iloc[0]:.1f}%",
                f"{metrics_df['Denial Utilization'].iloc[0]:.1f}%"
            ],
            'Month 1': [
                f"{metrics_df['Accounts'].iloc[1]:.0f}",
                "Met" if metrics_df['Submission SLA Met'].iloc[1] else "Not Met",
                "Met" if metrics_df['Denial SLA Met'].iloc[1] else "Not Met",
                f"{metrics_df['Submission Utilization'].iloc[1]:.1f}%",
                f"{metrics_df['Denial Utilization'].iloc[1]:.1f}%"
            ],
            'Month 2': [
                f"{metrics_df['Accounts'].iloc[2]:.0f}",
                "Met" if metrics_df['Submission SLA Met'].iloc[2] else "Not Met",
                "Met" if metrics_df['Denial SLA Met'].iloc[2] else "Not Met",
                f"{metrics_df['Submission Utilization'].iloc[2]:.1f}%",
                f"{metrics_df['Denial Utilization'].iloc[2]:.1f}%"
            ],
            'Month 3': [
                f"{metrics_df['Accounts'].iloc[3]:.0f}",
                "Met" if metrics_df['Submission SLA Met'].iloc[3] else "Not Met",
                "Met" if metrics_df['Denial SLA Met'].iloc[3] else "Not Met",
                f"{metrics_df['Submission Utilization'].iloc[3]:.1f}%",
                f"{metrics_df['Denial Utilization'].iloc[3]:.1f}%"
            ]
        })
        
        # Create utilization chart
        fig = go.Figure()
        
        for metric in ['Submission Utilization', 'Denial Utilization']:
            fig.add_trace(go.Bar(
                name=metric,
                x=['Month ' + str(i) for i in range(4)],
                y=metrics_df[metric],
                marker_color=self.colors['submission_analysts' if 'Submission' in metric else 'denial_analysts']
            ))
        
        fig.update_layout(
            title='Team Utilization',
            barmode='group',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Add target zone
        fig.add_hrect(
            y0=85, y1=95,
            fillcolor="green", opacity=0.1,
            layer="below", line_width=0,
            name="Target Zone"
        )
        
        return operational_summary, fig
    
    def generate_sensitivity_summary(self):
        """Generate sensitivity analysis summary"""
        # Run sensitivity analysis for key parameters
        utilization_sensitivity = self.optimizer.run_sensitivity_analysis(
            'max_utilization',
            [0.85, 0.90, 0.95]
        )
        
        # Format sensitivity table
        sensitivity_summary = pd.DataFrame({
            'Scenario': ['Conservative (85%)', 'Base Case (90%)', 'Aggressive (95%)'],
            'Total Staff': utilization_sensitivity['Total Staff'].round(0),
            'Net Margin': [f"${x:,.0f}" for x in utilization_sensitivity['Net Margin']],
            'Gross Margin %': [f"{x:.1f}%" for x in utilization_sensitivity['Gross Margin %']]
        })
        
        return sensitivity_summary

# Initialize dashboard
dashboard = RCMDashboard()

# Title and description
st.title("Commure RCM Scaling and Execution Plan")
st.markdown("""
This dashboard presents the data-driven analysis and optimization results for scaling RCM operations across 100 healthcare practices.
The plan has been optimized for maximum efficiency while maintaining quality standards and SLA compliance.
""")

# 1. Process and Organizational Build-Out
st.header("1. Process and Organizational Build-Out")

# Staffing Section
st.subheader("Core Structure and Roles")
staffing_data, staffing_chart = dashboard.generate_staffing_summary()
st.plotly_chart(staffing_chart, use_container_width=True)
st.markdown("""
### Staffing Details by Role
* **US Team**: GM, Hiring Lead, CS Lead, Implementation Lead
* **India Team**: Submission Analysts, Denial Analysts, Operations Managers, QC Lead
* **Support Functions**: HR + Recruiters, Implementation Team
""")
st.dataframe(staffing_data, use_container_width=True)

# 2. Metrics and KPIs
st.header("2. Metrics and KPIs")

# Financial Analysis
st.subheader("Financial Performance")
financial_summary, financial_chart = dashboard.generate_financial_summary()
st.plotly_chart(financial_chart, use_container_width=True)
st.markdown("""
### Key Financial Metrics
* Revenue growth and margin targets
* Labor and overhead cost structure
* Implementation and scaling costs
""")
st.dataframe(financial_summary, use_container_width=True)

# Operational Metrics
st.subheader("Operational Performance")
operational_summary, utilization_chart = dashboard.generate_operational_summary()
st.plotly_chart(utilization_chart, use_container_width=True)
st.markdown("""
### Key Operational Metrics
* SLA compliance rates
* Team utilization targets
* Quality metrics and error rates
""")
st.dataframe(operational_summary, use_container_width=True)

# 3. Execution Plan
st.header("3. Execution Plan")

# Implementation Timeline
st.subheader("Implementation Timeline")
st.markdown("""
### First 7 Days
* India office setup and legal compliance
* US leadership hiring
* India hiring pipeline launch
* Tooling and systems implementation

### First 30 Days
* Initial India team hiring (50-60%)
* Training program rollout
* First 10 accounts onboarding
* Metrics dashboard implementation

### First 60 Days
* Complete India operations hiring
* Implementation team scaling
* QA process refinement
* SLA monitoring and optimization

### First 90 Days
* Full operational capacity
* Process improvement review
* Team structure optimization
* Long-term scaling plan
""")

# Key Risks and Sensitivity
st.header("4. Key Risks & Sensitivity")
sensitivity_summary = dashboard.generate_sensitivity_summary()
st.markdown("""
### Risk Analysis
The model's sensitivity to key assumptions highlights potential risks and opportunities:
""")
st.dataframe(sensitivity_summary, use_container_width=True)

# Add implementation metrics
st.subheader("Implementation Metrics")
implementation_metrics = pd.DataFrame({
    'Metric': [
        'Time-to-go-live per account',
        'Accounts live vs. planned',
        'Training completion rate',
        'Claim approval rate',
        'Denial recovery rate',
        'SLA compliance rate',
        'Analyst utilization',
        'Error rate',
        'Customer satisfaction',
        'Account churn rate'
    ],
    'Target': [
        '14 days',
        '100%',
        '100%',
        '90%',
        '30%',
        '95%',
        '85-90%',
        '<2%',
        '>90%',
        '<5%'
    ],
    'Current': [
        f"{dashboard.model.IMPLEMENTATION_METRICS['onboarding_days_per_account']} days",
        f"{dashboard.monthly_accounts[-1]}/{dashboard.model.TOTAL_ACCOUNTS}",
        'In Progress',
        f"{dashboard.model.TARGET_APPROVAL_RATE*100:.1f}%",
        f"{dashboard.model.DENIAL_RECOVERY_RATE*100:.1f}%",
        f"{'Met' if dashboard.monthly_metrics[-1]['Submission SLA Met'] and dashboard.monthly_metrics[-1]['Denial SLA Met'] else 'Not Met'}",
        f"{dashboard.monthly_metrics[-1]['Submission Utilization']:.1f}%",
        f"{dashboard.monthly_metrics[-1].get('Error Rate', 0):.1f}%",
        'TBD',
        f"{dashboard.model.ACCOUNT_CHURN_RATE*100:.1f}%"
    ]
})
st.dataframe(implementation_metrics, use_container_width=True)

if __name__ == "__main__":
    print("Dashboard generated successfully!") 