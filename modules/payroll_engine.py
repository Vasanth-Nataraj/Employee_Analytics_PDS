"""
Payroll Engine Module
Implements statutory payroll rules, tax computations, and attendance deductions.
"""

calculate_hra = lambda basic: basic * 0.20  # House Rent Allowance (20%)
calculate_da = lambda basic: basic * 0.10   # Dearness Allowance (10%)
calculate_pf = lambda basic: basic * 0.12   # Provident Fund (12%)

TOTAL_WORKING_DAYS = 26

def calculate_income_tax(taxable_income: float) -> float:
    """Calculates income tax based on progressive tax slabs."""
    if taxable_income <= 250000:
        return 0.0
    elif taxable_income <= 500000:
        return (taxable_income - 250000) * 0.05
    elif taxable_income <= 1000000:
        return (250000 * 0.05) + ((taxable_income - 500000) * 0.20)
    else:
        return (250000 * 0.05) + (500000 * 0.20) + ((taxable_income - 1000000) * 0.30)

def calculate_attendance_deduction(days_present: int, basic_salary: float) -> tuple:
    """Calculates attendance percentage and deductions for unworked days beyond casual leave."""
    days = max(0, min(days_present, TOTAL_WORKING_DAYS))
    attendance_pct = (days / TOTAL_WORKING_DAYS) * 100
    daily_rate = basic_salary / TOTAL_WORKING_DAYS
    leaves_taken = TOTAL_WORKING_DAYS - days
    unpaid_leaves = max(0, leaves_taken - 2)
    deduction = unpaid_leaves * daily_rate
    return round(attendance_pct, 2), round(deduction, 2)