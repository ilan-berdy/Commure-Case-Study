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
        self.REVENUE_PERCENTAGE = 0.05  # 5% (case study requirement)
        self.TARGET_MARGIN = 0.60  # 60%
        
        # Revenue adjustments
        self.COLLECTION_RATE = 0.95  # 95% of approved claims are collected
        self.ACCOUNT_CHURN_RATE = 0.05  # 5% annual churn rate
        self.REVENUE_RAMP_UP = {
            1: 0.5,  # Month 1: 50% of target revenue
            2: 0.75, # Month 2: 75% of target revenue
            3: 1.0   # Month 3: 100% of target revenue
        }
        
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
        self.ANALYST_BASE_SALARY = 355  # Base monthly salary (India market rate)
        self.FULLY_LOADED_MULTIPLIER = 1.5  # Multiplier for benefits and overhead
        self.ANALYST_SALARY = self.ANALYST_BASE_SALARY * self.FULLY_LOADED_MULTIPLIER
        self.MANAGER_SALARY = self.ANALYST_SALARY * 1.5  # Manager salary at 1.5x analyst salary
        
        # One-time setup costs
        self.OFFICE_SETUP_COST = 50000  # One-time cost for office setup
        
        # Pre-quarter hiring team costs (Month 0)
        self.US_HIRING_LEAD_SALARY = 10000  # Monthly salary for US hiring lead
        self.INDIA_COUNTRY_MANAGER_SALARY = 798  # Monthly salary for India country manager
        self.INDIA_HR_RECRUITER_SALARY = 532  # Monthly salary for India HR/recruiter
        
        # Overhead costs (per staff member per month)
        self.SOFTWARE_COST_PER_ANALYST = 200  # Software licenses and tools
        self.OFFICE_COST_PER_ANALYST = 150    # Office space and utilities
        self.TRAINING_COST_PER_ANALYST = 50   # Ongoing training and development
        
        # Additional overhead costs (monthly)
        self.INFRASTRUCTURE_COST = 5000  # Servers, cloud services, etc.
        self.COMPLIANCE_COST = 3000      # Security, compliance, audits
        self.QA_COST = 2000              # Quality assurance and monitoring
        
        # Customer Success costs
        self.CUSTOMER_SUCCESS_COST = 3000  # Monthly cost for customer success team
        self.IMPLEMENTATION_COST = 2000    # Monthly cost for implementation team
        
        # Staff ratios
        self.ANALYSTS_PER_MANAGER = 12
        self.ACCOUNTS_PER_CUSTOMER_SUCCESS = 20  # 1 CS rep per 20 accounts
        
        # Denial recovery parameters
        self.DENIAL_RECOVERY_RATE = 0.30  # 30% of denials are recovered
        self.DENIAL_RECOVERY_COST_MULTIPLIER = 2.0  # Denial recovery costs 2x normal processing
        self.DENIAL_RECOVERY_VALUE_FACTOR = 0.8  # Recovered claims only bring 80% of full value
        
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
        self.MINUTES_PER_DAY = 480  # 8 hours
        self.AVAILABLE_TIME_FACTOR = 0.85  # 85% of time available for productive work
        
        # Analyst allocation between submission and denial work
        self.SUBMISSION_ALLOCATION = 0.85  # 85% of analysts on submission work
        self.DENIAL_ALLOCATION = 0.15  # 15% of analysts on denial work
        
        # Denial work ramp-up profile (weeks after start)
        self.DENIAL_RAMP_UP = {
            1: 0.0,    # Week 1: No denial work (all submissions)
            2: 0.0,    # Week 2: No denial work
            3: 0.25,   # Week 3: 25% of denial work
            4: 0.50,   # Week 4: 50% of denial work
            5: 0.75,   # Week 5: 75% of denial work
            6: 1.0     # Week 6+: Full denial work
        }
        
        # Implementation metrics
        self.IMPLEMENTATION_METRICS = {
            'onboarding_days_per_account': 14,  # days to onboard a new account
            'training_hours_per_analyst': 40,   # hours of training per new analyst
            'qa_review_rate': 0.10,            # 10% of claims reviewed by QA
            'trainer_ratio': 10,               # 1 trainer per 10 analysts
            'qa_analyst_ratio': 15,            # 1 QA analyst per 15 analysts
            'ramp_up_efficiency': {            # Efficiency during ramp-up
                1: 0.50,  # Month 1: 50% efficiency
                2: 0.75,  # Month 2: 75% efficiency
                3: 0.90   # Month 3: 90% efficiency
            }
        }
        
        # Quality metrics and costs
        self.QUALITY_METRICS = {
            'error_rate_target': 0.02,         # 2% target error rate
            'error_cost_multiplier': 2.0,      # Errors cost 2x normal processing
            'retraining_hours': 8,             # Hours needed for retraining
            'quality_bonus_threshold': 0.98,    # 98% accuracy for bonus
            'quality_bonus_amount': 50         # Monthly bonus amount in USD
        }
        
        # Hiring team structure
        self.HIRING_TEAM = {
            'us_hiring_lead': {
                'count': 1,
                'salary': 10000
            },
            'india_country_manager': {
                'count': 1,
                'salary': 798
            },
            'india_hr_recruiter': {
                'count': 2,
                'salary': 532
            },
            'india_trainer': {
                'salary': 665  # 25% more than analyst salary
            },
            'india_qa_analyst': {
                'salary': 598  # 12.5% more than analyst salary
            }
        }
        
        # Office setup and infrastructure
        self.OFFICE_SETUP = {
            'furniture_per_person': 200,      # Desk, chair, etc.
            'it_per_person': 300,             # Computer, peripherals
            'infrastructure': 15000,          # Network, servers, etc.
            'legal_and_registration': 10000,  # Legal fees, permits
            'renovation': 15000,              # Space renovation
            'amortization_months': 12         # Amortize over 12 months
        }
        
        # Calculate total office setup cost
        self.OFFICE_SETUP_COST = (
            self.OFFICE_SETUP['infrastructure'] +
            self.OFFICE_SETUP['legal_and_registration'] +
            self.OFFICE_SETUP['renovation']
        )
        
        # Calculate derived constants
        self.CLAIMS_PER_PRACTICE = self.TOTAL_CLAIMS_VALUE / (self.TOTAL_ACCOUNTS * self.AVG_CLAIM_VALUE)
        self.MINUTES_PER_MONTH = self.HOURS_PER_DAY * self.DAYS_PER_MONTH * self.MINUTES_PER_HOUR

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

    def calculate_implementation_staff(self, month, total_analysts, active_accounts):
        """Calculate implementation staff needed based on accounts and analysts."""
        if month == 0:
            return 0
            
        # Calculate trainers needed
        trainers_for_analysts = np.ceil(total_analysts / self.IMPLEMENTATION_METRICS['trainer_ratio'])
        
        # Calculate QA analysts needed
        qa_analysts = np.ceil(total_analysts / self.IMPLEMENTATION_METRICS['qa_analyst_ratio'])
        
        # Calculate account onboarding staff needed
        if month == 1:
            new_accounts = self.ACCOUNTS_MONTH1
        elif month == 2:
            new_accounts = self.ACCOUNTS_MONTH2
        else:  # month == 3
            new_accounts = self.ACCOUNTS_MONTH3
            
        onboarding_days = new_accounts * self.IMPLEMENTATION_METRICS['onboarding_days_per_account']
        onboarding_staff = np.ceil(onboarding_days / (self.DAYS_PER_MONTH * self.HOURS_PER_DAY))
        
        return int(trainers_for_analysts + qa_analysts + onboarding_staff)

    def calculate_monthly_metrics(self, month):
        """Calculate metrics for a given month (0-3)"""
        # Validate month input
        if not isinstance(month, int) or month < 0 or month > 3:
            raise ValueError("Month must be an integer between 0 and 3")
            
        # Calculate active accounts
        if month == 0:
            active_accounts = 0
        elif month == 1:
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
        daily_claims = monthly_claims / self.DAYS_PER_MONTH if self.DAYS_PER_MONTH > 0 else 0
        daily_denied_claims = denied_claims / self.DAYS_PER_MONTH if self.DAYS_PER_MONTH > 0 else 0
        
        # Calculate total analyst count needed
        total_minutes_needed = (
            (monthly_claims * base_time_per_claim) +  # Submission work
            (denied_claims * base_time_per_claim * 1.5)  # Denial work (50% more time)
        )
        
        # Target 85% utilization and add 5% buffer for volume spikes and training
        target_utilization = 0.85
        buffer_factor = 1.05  # Additional 5% capacity for spikes and training
        total_minutes_available_needed = (total_minutes_needed / target_utilization) * buffer_factor
        
        # Calculate total analysts needed based on available productive time
        total_analyst_count = np.ceil(
            total_minutes_available_needed / 
            (self.MINUTES_PER_MONTH * self.AVAILABLE_TIME_FACTOR)
        )
        
        # Ensure minimum staffing levels
        total_analyst_count = max(total_analyst_count, 2)  # At least 2 analysts for coverage
        
        # Split analysts between submission and denial work
        submission_analysts = np.ceil(total_analyst_count * self.SUBMISSION_ALLOCATION)
        denial_analysts = np.ceil(total_analyst_count * self.DENIAL_ALLOCATION)
        
        # Calculate manager count
        manager_count = np.ceil(total_analyst_count / self.ANALYSTS_PER_MANAGER)
        
        # Calculate monthly labor costs
        core_labor_cost = (
            (total_analyst_count * self.ANALYST_SALARY) +
            (manager_count * self.MANAGER_SALARY)
        )
        
        # Add hiring team costs for month 0
        if month == 0:
            hiring_team_cost = (
                self.US_HIRING_LEAD_SALARY +
                self.INDIA_COUNTRY_MANAGER_SALARY +
                (2 * self.INDIA_HR_RECRUITER_SALARY)
            )
            total_labor_cost = hiring_team_cost
        else:
            hiring_team_cost = 0
            total_labor_cost = core_labor_cost
        
        # Calculate overhead costs
        total_staff = total_analyst_count + manager_count
        software_cost = total_staff * self.SOFTWARE_COST_PER_ANALYST
        office_cost = total_staff * self.OFFICE_COST_PER_ANALYST
        training_cost = total_staff * self.TRAINING_COST_PER_ANALYST
        
        # Additional overhead costs
        infrastructure_cost = self.INFRASTRUCTURE_COST
        compliance_cost = self.COMPLIANCE_COST
        qa_cost = self.QA_COST
        
        # Calculate total overhead
        total_overhead = (
            software_cost +
            office_cost +
            training_cost +
            infrastructure_cost +
            compliance_cost +
            qa_cost
        )
        
        # Calculate revenue
        monthly_revenue = approved_claims * self.AVG_CLAIM_VALUE * self.REVENUE_PERCENTAGE
        
        # Calculate gross margin
        gross_margin = ((monthly_revenue - total_labor_cost - total_overhead) / monthly_revenue) * 100 if monthly_revenue > 0 else 0
        
        # Calculate capacity and SLA metrics
        submission_minutes_per_day = submission_analysts * self.MINUTES_PER_DAY * self.AVAILABLE_TIME_FACTOR
        denial_minutes_per_day = denial_analysts * self.MINUTES_PER_DAY * self.AVAILABLE_TIME_FACTOR
        
        # Calculate minutes needed per day for each stream
        submission_minutes_needed = daily_claims * base_time_per_claim
        denial_minutes_needed = daily_denied_claims * (base_time_per_claim * 1.5)
        
        # Debug logging
        print(f"\nMonth {month} Utilization Analysis:")
        print(f"Submission Analysts: {submission_analysts}")
        print(f"Denial Analysts: {denial_analysts}")
        print(f"Daily Claims: {daily_claims:.1f}")
        print(f"Daily Denied Claims: {daily_denied_claims:.1f}")
        print(f"Time per Claim: {base_time_per_claim:.1f} minutes")
        print(f"Time per Denial: {base_time_per_claim * 1.5:.1f} minutes")
        print(f"\nSubmission Stream:")
        print(f"Minutes Needed per Day: {submission_minutes_needed:.1f}")
        print(f"Minutes Available per Day: {submission_minutes_per_day:.1f}")
        print(f"Submission Utilization: {(submission_minutes_needed/submission_minutes_per_day*100):.1f}%")
        print(f"\nDenial Stream:")
        print(f"Minutes Needed per Day: {denial_minutes_needed:.1f}")
        print(f"Minutes Available per Day: {denial_minutes_per_day:.1f}")
        print(f"Denial Utilization: {(denial_minutes_needed/denial_minutes_per_day*100):.1f}%")
        
        # Calculate capacity utilization for each stream
        submission_utilization = min((submission_minutes_needed / submission_minutes_per_day) * 100 if submission_minutes_per_day > 0 else 0, 100)
        denial_utilization = min((denial_minutes_needed / denial_minutes_per_day) * 100 if denial_minutes_per_day > 0 else 0, 100)
        
        # Check SLA compliance
        submission_sla_met = submission_minutes_needed <= (submission_minutes_per_day * self.SUBMISSION_SLA)
        denial_sla_met = denial_minutes_needed <= (denial_minutes_per_day * self.DENIAL_WORK_SLA)
        
        # Calculate implementation staff
        implementation_staff = self.calculate_implementation_staff(
            month, 
            total_analyst_count,
            active_accounts
        )
        
        # Calculate quality metrics
        if month > 0:
            efficiency = self.IMPLEMENTATION_METRICS['ramp_up_efficiency'].get(month, 0.90)
            error_rate = (1 - efficiency) * 2  # Double the inefficiency as error rate
            quality_bonus_eligible = error_rate <= (1 - self.QUALITY_METRICS['quality_bonus_threshold'])
            quality_bonus_cost = (
                total_analyst_count * 
                self.QUALITY_METRICS['quality_bonus_amount'] if quality_bonus_eligible else 0
            )
            error_cost = (
                monthly_claims * 
                error_rate * 
                self.QUALITY_METRICS['error_cost_multiplier'] * 
                base_time_per_claim
            )
        else:
            quality_bonus_cost = 0
            error_cost = 0
        
        # Update the metrics dictionary
        metrics = {
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
            'Core Labor Cost': core_labor_cost,
            'Hiring Team Cost': hiring_team_cost,
            'Total Labor Cost': total_labor_cost,
            'Monthly Revenue': monthly_revenue,
            'Gross Margin %': gross_margin,
            'Submission SLA Met': submission_sla_met,
            'Denial SLA Met': denial_sla_met,
            'Submission Utilization %': submission_utilization,
            'Denial Utilization %': denial_utilization,
            'Implementation Staff': implementation_staff,
            'Quality Bonus Cost': quality_bonus_cost,
            'Error Cost': error_cost,
            'Efficiency Rate': efficiency if month > 0 else 0,
            'Error Rate': error_rate if month > 0 else 0,
            # Add overhead costs
            'Software Cost': software_cost,
            'Office Cost': office_cost,
            'Training Cost': training_cost,
            'Infrastructure Cost': infrastructure_cost,
            'Compliance Cost': compliance_cost,
            'QA Cost': qa_cost,
            'Total Overhead': total_overhead
        }
        
        return metrics

    def generate_report(self):
        """Generate a report for all three months"""
        data = [self.calculate_monthly_metrics(month) for month in range(0, 4)]
        return pd.DataFrame(data)

if __name__ == "__main__":
    # Create model instance
    model = SimpleRCMModel()
    
    # Generate and display report
    report = model.generate_report()
    print("\n=== Simple RCM Capacity Planning Model Results ===\n")
    print(report.to_string()) 