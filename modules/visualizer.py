"""
Visualizer Module
Generates analytical charts and master reporting dashboards.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class Visualizer:
    def __init__(self, df: pd.DataFrame, output_dir: str = "outputs"):
        self.df = df
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        sns.set_theme(style="whitegrid", palette="muted")

    def plot_unified_dashboard(self):
        """Builds a comprehensive 4-panel workforce analytics dashboard."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 11))
        fig.suptitle("WORKFORCE PERFORMANCE & COMPENSATION ANALYTICS", fontsize=15, fontweight="bold")

        # 1. Salary Distribution & Density
        sns.histplot(self.df["Basic_Salary"], kde=True, ax=axes[0, 0], color="#2563eb", bins=22)
        median_sal = self.df["Basic_Salary"].median()
        axes[0, 0].axvline(median_sal, color="crimson", linestyle="--", linewidth=1.8, label=f"Median: INR {median_sal:,.0f}")
        axes[0, 0].set_title("Basic Salary Distribution (Density & Spread)", fontweight="semibold")
        axes[0, 0].set_xlabel("Basic Salary (INR)")
        axes[0, 0].set_ylabel("Employee Count")
        axes[0, 0].legend()

        # 2. Departmental Net Salary Spread
        sns.boxplot(data=self.df, x="Department", y="Net_Salary", ax=axes[0, 1], palette="Set2")
        sns.stripplot(data=self.df, x="Department", y="Net_Salary", ax=axes[0, 1], color="black", alpha=0.25, jitter=0.2)
        axes[0, 1].set_title("Departmental Net Take-Home Spread & Variance", fontweight="semibold")
        axes[0, 1].set_xlabel("Department")
        axes[0, 1].set_ylabel("Net Salary (INR)")

        # 3. Experience vs. Base Salary Regression
        sns.regplot(
            data=self.df,
            x="Experience_Years",
            y="Basic_Salary",
            ax=axes[1, 0],
            color="#059669",
            scatter_kws={"alpha": 0.5, "s": 30},
            line_kws={"color": "#dc2626", "linewidth": 2}
        )
        axes[1, 0].set_title("Experience vs. Base Salary Trajectory", fontweight="semibold")
        axes[1, 0].set_xlabel("Experience (Years)")
        axes[1, 0].set_ylabel("Basic Salary (INR)")

        # 4. Correlation Heatmap
        corr_cols = ["Experience_Years", "Basic_Salary", "Days_Present", "Performance_Score", "Net_Salary"]
        corr_mat = self.df[corr_cols].corr()
        sns.heatmap(corr_mat, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, ax=axes[1, 1], linewidths=0.5)
        axes[1, 1].set_title("Workforce Feature Correlation Heatmap", fontweight="semibold")

        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        dashboard_path = os.path.join(self.output_dir, "master_analytics_dashboard.png")
        plt.savefig(dashboard_path, dpi=300)
        print(f"Master dashboard exported to '{dashboard_path}'.")
        plt.show()

    def plot_attendance_vs_performance_bubble(self):
        """Displays attendance impact on performance appraisals."""
        plt.figure(figsize=(9, 5))
        sns.scatterplot(
            data=self.df,
            x="Attendance_Pct",
            y="Performance_Score",
            hue="Department",
            size="Net_Salary",
            sizes=(30, 200),
            alpha=0.75
        )
        plt.title("Attendance Rate vs. Performance Score by Department", fontweight="bold")
        plt.xlabel("Attendance Rate (%)")
        plt.ylabel("Performance Score (1.0 - 5.0)")
        plt.tight_layout()
        output_bubble = os.path.join(self.output_dir, "attendance_performance_matrix.png")
        plt.savefig(output_bubble, dpi=300)
        print(f"Plot saved to '{output_bubble}'.")
        plt.show()