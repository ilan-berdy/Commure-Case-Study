# RCM Capacity Planning Model

A simple capacity planning model for Revenue Cycle Management (RCM) operations.

## Overview

This project provides a simplified model for planning RCM operations, including:
- Staffing requirements
- Cost calculations
- Revenue projections
- SLA compliance checks

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the dashboard:
```bash
streamlit run simple_rcm_dashboard.py
```

## Project Structure

- `simple_rcm_model.py`: Core model implementation
- `simple_rcm_dashboard.py`: Streamlit dashboard
- `requirements.txt`: Project dependencies

## Model Assumptions

### Core Assumptions (from Case Study)
- 100 total accounts with $200M total claims value
- $200 average claim value
- 5% revenue percentage
- 60% target margin
- 90% dollar approval rate
- 2-5 minutes per process step
- Account onboarding schedule: 10/30/60 over 3 months
- SLAs: 5 days for submission, 3 days for denial work
- India-based analysts and managers

### Additional Model Assumptions
- 85% utilization factor for analysts
- 8 hours per day, 22 working days per month
- 1 manager per 8 analysts
- Analyst salary: $5,400/month
- Manager salary: $8,100/month
- No learning curve impact
- No QA staff included
- No training time included
- Even distribution of claims
- All claims have same complexity
- No staff turnover impact 