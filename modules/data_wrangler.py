"""
Data Wrangler Module
Handles dataset ingestion, data cleaning, automated payroll derivations, and aggregation matrices.
"""

import os
import numpy as np
import pandas as pd
from .payroll_engine import calculate_hra, calculate_da, calculate_pf, calculate_income_tax

class DataWrangler:
    def __init__(self, data_path: str = "data/employees_dataset.csv"):
        self.data_path = data_path
        self.df = None
        self._ensure_dataset_exists()

    def _ensure_dataset_exists(self):
        """Generates a realistic 250-record dataset if CSV is missing."""
        if not os.path.exists(self.data_path):
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            np.random.seed(42)
            n = 250

            emp_ids = np.arange(1001, 1001 + n)
            departments = np.random.choice(
                ["Engineering", "Analytics", "HR", "Sales", "Finance"],
                size=n,
                p=[0.35, 0.20, 0.15, 0.15, 0.15]
            )
            gender = np.random.choice(["Male", "Female"], size=n, p=[0.55, 0.45])
            experience = np.round(np.clip(np.random.gamma(shape=3.0, scale=1.5, size=n), 0.5, 20.0), 1)
            
            # Base salary with realistic variance
            base_salaries = np.round(np.clip(32000 + (experience * 10500) + np.random.normal(0, 8000, size=n), 28000, 240000), 2)
            perf_scores = np.round(np.clip(np.random.normal(loc=3.6, scale=0.7, size=n), 1.0, 5.0), 1)
            days_present = np.random.binomial(n=26, p=0.92, size=n)

            # Injected missing values to demonstrate data cleaning
            mask_missing_salaries = np.random.choice([True, False], size=n, p=[0.06, 0.94])
            mask_missing_ratings = np.random.choice([True, False], size=n, p=[0.04, 0.96])

            raw_df = pd.DataFrame({
                "Employee_ID": emp_ids,
                "Department": departments,
                "Gender": gender,
                "Experience_Years": experience,
                "Basic_Salary": np.where(mask_missing_salaries, np.nan, base_salaries),
                "Days_Present": days_present,
                "Performance_Score": np.where(mask_missing_ratings, np.nan, perf_scores)
            })
            raw_df.to_csv(self.data_path, index=False)
            print(f"Initialized dataset at '{self.data_path}' with {n} records.")

    def load_and_wrangle(self) -> pd.DataFrame:
        """Executes data cleaning, missing value imputation, and payroll calculations."""
        self.df = pd.read_csv(self.data_path)
        print(f"Ingested dataset: {self.df.shape[0]} rows x {self.df.shape[1]} columns.")

        # 1. Missing Value Imputation
        null_counts = self.df.isnull().sum()
        if null_counts.sum() > 0:
            print("Missing values detected:\n", null_counts[null_counts > 0].to_dict())

        # Impute salary using Departmental Median; Rating using Mean
        dept_median = self.df.groupby("Department")["Basic_Salary"].transform("median")
        self.df["Basic_Salary"] = self.df["Basic_Salary"].fillna(dept_median)
        self.df["Performance_Score"] = self.df["Performance_Score"].fillna(round(self.df["Performance_Score"].mean(), 1))

        # 2. Outlier Detection via Z-Scores (> 2.5 sigma)
        salary_vals = self.df["Basic_Salary"].to_numpy()
        mean_s, std_s = np.mean(salary_vals), np.std(salary_vals)
        z_scores = np.abs((salary_vals - mean_s) / std_s)
        self.df["Is_Salary_Outlier"] = z_scores > 2.5
        print(f"Detected {self.df['Is_Salary_Outlier'].sum()} salary records deviating > 2.5 std deviations.")

        # 3. Vectorized Payroll & Tax Calculations
        self.df["HRA"] = calculate_hra(self.df["Basic_Salary"])
        self.df["DA"] = calculate_da(self.df["Basic_Salary"])
        self.df["PF"] = calculate_pf(self.df["Basic_Salary"])

        # Attendance Deductions
        daily_rate = self.df["Basic_Salary"] / 26
        unpaid_days = np.maximum(0, (26 - self.df["Days_Present"]) - 2)
        self.df["Attendance_Penalty"] = np.round(unpaid_days * daily_rate, 2)
        self.df["Attendance_Pct"] = np.round((self.df["Days_Present"] / 26) * 100, 2)

        # Performance Bonuses
        bonus_conditions = [
            (self.df["Performance_Score"] >= 4.5),
            (self.df["Performance_Score"] >= 3.5)
        ]
        bonus_rates = [0.15, 0.08]
        self.df["Bonus"] = self.df["Basic_Salary"] * np.select(bonus_conditions, bonus_rates, default=0.0)

        # Gross, Tax & Take-Home Salary
        self.df["Gross_Salary"] = self.df["Basic_Salary"] + self.df["HRA"] + self.df["DA"] + self.df["Bonus"]
        annual_taxable = (self.df["Gross_Salary"] - self.df["PF"]) * 12
        self.df["Monthly_Tax"] = annual_taxable.apply(lambda x: round(calculate_income_tax(x) / 12, 2))
        self.df["Net_Salary"] = np.round(self.df["Gross_Salary"] - self.df["PF"] - self.df["Monthly_Tax"] - self.df["Attendance_Penalty"], 2)

        # Career Stage Bins
        self.df["Career_Stage"] = pd.cut(
            self.df["Experience_Years"],
            bins=[0, 3, 7, 12, 30],
            labels=["Entry-Level (0-3y)", "Mid-Level (4-7y)", "Senior (8-12y)", "Lead/Principal (>12y)"]
        )

        return self.df

    def get_department_aggregation(self) -> pd.DataFrame:
        """Groups data by department and returns summary metrics."""
        return self.df.groupby("Department").agg(
            Headcount=("Employee_ID", "count"),
            Median_Basic=("Basic_Salary", "median"),
            Mean_Net_Salary=("Net_Salary", "mean"),
            Mean_Experience=("Experience_Years", "mean"),
            Mean_Attendance_Pct=("Attendance_Pct", "mean"),
            Mean_Performance=("Performance_Score", "mean")
        ).round(2)

    def get_pivot_table_analysis(self) -> pd.DataFrame:
        """Cross-tabulates Net Salary across Department and Career Stage."""
        return pd.pivot_table(
            self.df,
            values="Net_Salary",
            index="Department",
            columns="Career_Stage",
            aggfunc=np.median,
            fill_value=0
        ).round(2)