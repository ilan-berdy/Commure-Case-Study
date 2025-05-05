import pandas as pd
import numpy as np

class SimpleRCMModel:
    def __init__(self):
        """
        Simple RCM Capacity Planning Model
        
        Core Assumptions from Case Study:
        - 100 total accounts with $200M total claims value
        - $200 average claim value
        - 5% revenue percentage
        - 60% target margin
        - 90% dollar approval rate
        - 2-5 minutes per process step
        - Account onboarding schedule: 10/30/60 over 3 months
        - SLAs: 5 days for submission, 3 days for denial work
        - India-based analysts and managers
        """
        
        # ===== CORE CONSTANTS FROM CASE STUDY =====
        # Financial parameters
        self.TOTAL_ACCOUNTS = 100
        self.TOTAL_CLAIMS_VALUE = 200000000  # $200M
        self.AVG_CLAIM_VALUE = 200  # dollars
        self.REVENUE_PERCENTAGE = 0.05  # 5%
        self.TARGET_MARGIN = 0.60  # 60%
        
        # Quality requirements
        self.TARGET_APPROVAL_RATE = 0.90  # 90%
        
        # Process time range
        self.MIN_TIME_PER_STEP = 2  # minutes
        self.MAX_TIME_PER_STEP = 5  # minutes
        
        # Account onboarding schedule
        self.ACCOUNTS_MONTH1 = 10
        self.ACCOUNTS_MONTH2 = 30
        self.ACCOUNTS_MONTH3 = 60
        
        # Labor costs (Monthly salaries in USD)
        self.ANALYST_BASE_SALARY = 500  # Base monthly salary
        self.FULLY_LOADED_MULTIPLIER = 1.5  # Multiplier for benefits and overhead
        self.ANALYST_SALARY = self.ANALYST_BASE_SALARY * self.FULLY_LOADED_MULTIPLIER  # $750 fully loaded cost
        self.MANAGER_SALARY = self.ANALYST_SALARY * 1.5  # $1,125 fully loaded cost
        
        # Process steps
        self.PROCESS_STEPS = [
            'Extract Encounters',
            'Submit Claims',
            'Reconcile',
            'Denial Analysis',
            'Resubmission'
        ]
        
        # Basic time constants
        self.HOURS_PER_DAY = 8
        self.DAYS_PER_MONTH = 22  # Standard working days
        self.MINUTES_PER_HOUR = 60
        
        # Calculate derived constants
        self.CLAIMS_PER_PRACTICE = self._calculate_claims_per_practice()
        self.MINUTES_PER_MONTH = self._calculate_minutes_per_month()
        self.DENIAL_RATE = 1 - self.TARGET_APPROVAL_RATE

    def _calculate_claims_per_practice(self):
        """Calculate claims per practice based on total claims value and average claim value"""
        total_claims = self.TOTAL_CLAIMS_VALUE / self.AVG_CLAIM_VALUE
        return total_claims / self.TOTAL_ACCOUNTS

    def _calculate_minutes_per_month(self):
        """Calculate available minutes per month based on standard work schedule"""
        return self.HOURS_PER_DAY * self.DAYS_PER_MONTH * self.MINUTES_PER_HOUR

    def calculate_monthly_metrics(self, month):
        """Calculate metrics for a given month (1-3)"""
        # Validate month input
        if not isinstance(month, int) or month < 1 or month > 3:
            raise ValueError("Month must be an integer between 1 and 3")
            
        # Calculate active accounts
        if month == 1:
            active_accounts = self.ACCOUNTS_MONTH1
        elif month == 2:
            active_accounts = self.ACCOUNTS_MONTH1 + self.ACCOUNTS_MONTH2
        else:  # month == 3
            active_accounts = self.ACCOUNTS_MONTH1 + self.ACCOUNTS_MONTH2 + self.ACCOUNTS_MONTH3
        
        # Calculate monthly claim volume
        monthly_claims = (active_accounts * self.CLAIMS_PER_PRACTICE) / 12
        
        # Calculate time per claim (range of 10-25 minutes)
        min_time_per_claim = self.MIN_TIME_PER_STEP * len(self.PROCESS_STEPS)  # 2 min × 5 steps = 10 min
        max_time_per_claim = self.MAX_TIME_PER_STEP * len(self.PROCESS_STEPS)  # 5 min × 5 steps = 25 min
        avg_time_per_claim = (min_time_per_claim + max_time_per_claim) / 2  # 17.5 min average
        
        # Calculate total time needed using average time
        total_minutes_needed = monthly_claims * avg_time_per_claim
        
        # Calculate required analyst headcount
        analyst_count = np.ceil(total_minutes_needed / self.MINUTES_PER_MONTH)
        
        # Calculate manager headcount (1 manager per 12 analysts)
        manager_count = np.ceil(analyst_count / 12)
        
        # Calculate monthly labor costs
        labor_cost = (
            (analyst_count * self.ANALYST_SALARY) +
            (manager_count * self.MANAGER_SALARY)
        )
        
        # Calculate revenue (5% of total claims value for active accounts)
        total_claims_value = monthly_claims * self.AVG_CLAIM_VALUE
        monthly_revenue = total_claims_value * self.REVENUE_PERCENTAGE
        
        # Calculate gross margin
        gross_margin = ((monthly_revenue - labor_cost) / monthly_revenue) * 100 if monthly_revenue > 0 else 0
        
        # Calculate SLA compliance
        daily_claims = monthly_claims / self.DAYS_PER_MONTH
        claims_per_analyst_per_day = self.MINUTES_PER_MONTH / (self.DAYS_PER_MONTH * avg_time_per_claim)
        sla_compliant = claims_per_analyst_per_day * analyst_count >= daily_claims
        
        return {
            'Month': month,
            'Active Accounts': active_accounts,
            'Monthly Claims': monthly_claims,
            'Daily Claims': daily_claims,
            'Claims per Analyst per Day': claims_per_analyst_per_day,
            'Total Time per Claim (min)': avg_time_per_claim,
            'Analyst Count': analyst_count,
            'Manager Count': manager_count,
            'Labor Cost': labor_cost,
            'Monthly Revenue': monthly_revenue,
            'Gross Margin %': gross_margin,
            'SLA Compliance': 'Yes' if sla_compliant else 'No'
        }

    def generate_report(self):
        """Generate a report for all three months"""
        data = [self.calculate_monthly_metrics(month) for month in range(1, 4)]
        return pd.DataFrame(data)

if __name__ == "__main__":
    # Create model instance
    model = SimpleRCMModel()
    
    # Generate and display report
    report = model.generate_report()
    print("\n=== Simple RCM Capacity Planning Model Results ===\n")
    print(report.to_string()) 