# Simple RCM Capacity Planning Model (Basic Version)

A minimal implementation of the RCM capacity planning model, focusing only on core operational requirements from the case study. This is a simplified version that excludes complex features like learning curves, quality metrics, and optimization.

## Core Assumptions

### Account Structure
- 100 total accounts
- Onboarding schedule: 10/30/60 over 3 months
- $200M total claims value
- $200 average claim value

### Process Parameters
- 5 process steps (2-5 minutes each):
  1. Extract Encounters
  2. Submit Claims
  3. Reconcile
  4. Denial Analysis
  5. Resubmission
- 90% dollar approval rate target
- SLAs: 5 days for submission, 3 days for denial work

### Financial Parameters
- 5% revenue percentage
- Target 60% gross margin
- India-based labor:
  - Analysts: $750/month (fully loaded)
  - Managers: $1,125/month (fully loaded)
- Manager ratio: 1:12

## What's Not Included (Simplifications)
- No learning curve for new staff
- No quality control team
- No training time/costs
- No customer success team
- No tools/systems costs
- No office/facility costs
- No US management costs
- No risk factors or contingencies
- No process improvements over time
- No customer churn risk

## Usage

```python
from simple_rcm_model import SimpleRCMModel

# Create model instance
model = SimpleRCMModel()

# Generate report
report = model.generate_report()
print(report)
```

## Requirements
- Python 3.6+
- pandas
- numpy

Install dependencies:
```bash
pip install -r requirements.simple.txt
```

## Project Structure

- `simple_rcm_model.py`: Core model implementation
- `simple_rcm_dashboard.py`: Streamlit dashboard
- `requirements.simple.txt`: Project dependencies

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