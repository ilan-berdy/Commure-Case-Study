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
        - 90% dollar approval rate target (final outcome)
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
        self.TARGET_APPROVAL_RATE = 0.90  # 90% final approval rate target
        self.DENIAL_RATE = 0.10  # 10% denial rate (1 - approval rate)
        
        # Process time range (minutes)
        self.MIN_TIME_PER_STEP = 2
        self.MAX_TIME_PER_STEP = 5
        
        # SLA requirements (days)
        self.SUBMISSION_SLA = 5  # days to submit claims
        self.DENIAL_WORK_SLA = 3  # days to work denials
        
        # Account onboarding schedule
        self.ACCOUNTS_MONTH1 = 10
        self.ACCOUNTS_MONTH2 = 30
        self.ACCOUNTS_MONTH3 = 60
        
        # Labor costs (Monthly salaries in USD)
        self.ANALYST_BASE_SALARY = 500  # Base monthly salary
        self.FULLY_LOADED_MULTIPLIER = 1.5  # Multiplier for benefits and overhead
        self.ANALYST_SALARY = self.ANALYST_BASE_SALARY * self.FULLY_LOADED_MULTIPLIER
        self.MANAGER_SALARY = self.ANALYST_SALARY * 1.5
        
        # Staff ratios
        self.ANALYSTS_PER_MANAGER = 12
        
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
        
        # Analyst allocation between submission and denial work
        self.SUBMISSION_ALLOCATION = 0.70  # 70% of analysts on submission work
        self.DENIAL_ALLOCATION = 0.30  # 30% of analysts on denial work
        
        # Denial work ramp-up profile (weeks after start)
        self.DENIAL_RAMP_UP = {
            1: 0.0,    # Week 1: No denial work (all submissions)
            2: 0.0,    # Week 2: No denial work
            3: 0.25,   # Week 3: 25% of denial work
            4: 0.50,   # Week 4: 50% of denial work
            5: 0.75,   # Week 5: 75% of denial work
            6: 1.0     # Week 6+: Full denial work
        }
        
        # Calculate derived constants
        self.CLAIMS_PER_PRACTICE = self._calculate_claims_per_practice()
        self.MINUTES_PER_MONTH = self._calculate_minutes_per_month()
        self.MINUTES_PER_DAY = self._calculate_minutes_per_day()

    def _calculate_claims_per_practice(self):
        """Calculate claims per practice based on total claims value and average claim value"""
        total_claims = self.TOTAL_CLAIMS_VALUE / self.AVG_CLAIM_VALUE
        return total_claims / self.TOTAL_ACCOUNTS

    def _calculate_minutes_per_month(self):
        """Calculate available minutes per month based on standard work schedule"""
        return self.HOURS_PER_DAY * self.DAYS_PER_MONTH * self.MINUTES_PER_HOUR

    def _calculate_minutes_per_day(self):
        """Calculate available minutes per day"""
        return self.HOURS_PER_DAY * self.MINUTES_PER_HOUR

    def _get_denial_ramp_up_factor(self, week):
        """Get the denial work ramp-up factor for a given week"""
        return self.DENIAL_RAMP_UP.get(week, 1.0)  # Default to full capacity after week 6

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
        
        # Calculate approved and denied claims based on target approval rate
        approved_claims = monthly_claims * self.TARGET_APPROVAL_RATE
        denied_claims = monthly_claims * self.DENIAL_RATE
        
        # Calculate average time per claim
        avg_time_per_step = (self.MIN_TIME_PER_STEP + self.MAX_TIME_PER_STEP) / 2
        base_time_per_claim = avg_time_per_step * len(self.PROCESS_STEPS)
        
        # Calculate daily volumes
        daily_claims = monthly_claims / self.DAYS_PER_MONTH
        daily_denied_claims = denied_claims / self.DAYS_PER_MONTH
        
        # Calculate total analyst count needed
        total_minutes_needed = (
            (monthly_claims * base_time_per_claim) +  # Submission work
            (denied_claims * base_time_per_claim * 1.5)  # Denial work (50% more time)
        )
        total_analyst_count = np.ceil(total_minutes_needed / self.MINUTES_PER_MONTH)
        
        # Split analysts between submission and denial work
        submission_analysts = np.ceil(total_analyst_count * self.SUBMISSION_ALLOCATION)
        denial_analysts = np.ceil(total_analyst_count * self.DENIAL_ALLOCATION)
        
        # Calculate manager count
        manager_count = np.ceil(total_analyst_count / self.ANALYSTS_PER_MANAGER)
        
        # Calculate monthly labor costs
        labor_cost = (
            (total_analyst_count * self.ANALYST_SALARY) +
            (manager_count * self.MANAGER_SALARY)
        )
        
        # Calculate revenue
        monthly_revenue = approved_claims * self.AVG_CLAIM_VALUE * self.REVENUE_PERCENTAGE
        
        # Calculate gross margin
        gross_margin = ((monthly_revenue - labor_cost) / monthly_revenue) * 100 if monthly_revenue > 0 else 0
        
        # Calculate capacity and SLA metrics
        submission_minutes_per_day = submission_analysts * self.MINUTES_PER_DAY
        denial_minutes_per_day = denial_analysts * self.MINUTES_PER_DAY
        
        # Calculate minutes needed per day for each stream
        submission_minutes_needed = daily_claims * base_time_per_claim
        denial_minutes_needed = daily_denied_claims * (base_time_per_claim * 1.5)
        
        # Calculate capacity utilization for each stream
        submission_utilization = (submission_minutes_needed / submission_minutes_per_day) * 100
        denial_utilization = (denial_minutes_needed / denial_minutes_per_day) * 100
        
        # Check SLA compliance
        submission_sla_met = submission_minutes_needed <= (submission_minutes_per_day * self.SUBMISSION_SLA)
        denial_sla_met = denial_minutes_needed <= (denial_minutes_per_day * self.DENIAL_WORK_SLA)
        
        # Calculate weekly metrics for denial work ramp-up
        weekly_denial_metrics = {}
        for week in range(1, 13):  # Calculate for 12 weeks
            ramp_up_factor = self._get_denial_ramp_up_factor(week)
            weekly_denial_claims = (denied_claims / 4) * ramp_up_factor  # Divide monthly by 4 for weekly
            weekly_denial_minutes = weekly_denial_claims * (base_time_per_claim * 1.5)
            weekly_denial_capacity = denial_minutes_per_day * 5 * ramp_up_factor  # 5 working days per week
            
            # Calculate effective submission capacity including denial analysts working on submissions
            effective_submission_capacity = submission_minutes_per_day + (denial_minutes_per_day * (1 - ramp_up_factor))
            weekly_submission_claims = (monthly_claims / 4)  # Divide monthly by 4 for weekly
            weekly_submission_minutes = weekly_submission_claims * base_time_per_claim
            weekly_submission_utilization = (weekly_submission_minutes / effective_submission_capacity) * 100
            
            weekly_denial_metrics[f'Week_{week}'] = {
                'Denial_Claims': weekly_denial_claims,
                'Minutes_Needed': weekly_denial_minutes,
                'Capacity': weekly_denial_capacity,
                'Utilization': (weekly_denial_minutes / weekly_denial_capacity) * 100 if weekly_denial_capacity > 0 else 0,
                'Effective_Submission_Capacity': effective_submission_capacity,
                'Submission_Utilization': weekly_submission_utilization
            }
        
        return {
            'Month': month,
            'Active Accounts': active_accounts,
            'Monthly Claims': monthly_claims,
            'Approved Claims': approved_claims,
            'Denied Claims': denied_claims,
            'Approval Rate': self.TARGET_APPROVAL_RATE * 100,
            'Time per Claim (min)': base_time_per_claim,
            'Daily Claims': daily_claims,
            'Daily Denied Claims': daily_denied_claims,
            'Total Analyst Count': total_analyst_count,
            'Submission Analysts': submission_analysts,
            'Denial Analysts': denial_analysts,
            'Manager Count': manager_count,
            'Labor Cost': labor_cost,
            'Monthly Revenue': monthly_revenue,
            'Gross Margin %': gross_margin,
            'Submission SLA Met': submission_sla_met,
            'Denial SLA Met': denial_sla_met,
            'Submission Utilization %': submission_utilization,
            'Denial Utilization %': denial_utilization,
            'Weekly Denial Metrics': weekly_denial_metrics
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