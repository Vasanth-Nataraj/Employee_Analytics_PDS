"""
Employee Analytics System
Enterprise workforce analytics and payroll processing pipeline.
"""

from modules.data_wrangler import DataWrangler
from modules.visualizer import Visualizer

def main():
    print("=" * 65)
    print("       EMPLOYEE PERFORMANCE & PAYROLL ANALYTICS SUITE")
    print("=" * 65)

    wrangler = DataWrangler()
    df = wrangler.load_and_wrangle()
    visualizer = Visualizer(df)

    while True:
        print("\n" + "=" * 55)
        print("                   ANALYTICS MENU")
        print("=" * 55)
        print(" 1. View Dataset Overview & Summary Statistics")
        print(" 2. Display Departmental Performance & Compensation")
        print(" 3. View Compensation Matrix by Career Stage (Pivot)")
        print(" 4. Launch Master 4-Panel Analytics Dashboard")
        print(" 5. Render Attendance vs Performance Matrix")
        print(" 6. Export Processed Payroll Records to CSV")
        print(" 7. Exit")
        print("=" * 55)

        choice = input("Select an option (1-7): ").strip()

        if choice == "1":
            print("\n--- DATASET STRUCTURE ---")
            print(df.info())
            print("\n--- DESCRIPTIVE STATISTICS ---")
            print(df[["Experience_Years", "Basic_Salary", "Performance_Score", "Net_Salary"]].describe().round(2))

        elif choice == "2":
            print("\n--- DEPARTMENTAL AGGREGATIONS ---")
            print(wrangler.get_department_aggregation())

        elif choice == "3":
            print("\n--- MEDIAN NET SALARY: DEPARTMENT VS CAREER STAGE ---")
            print(wrangler.get_pivot_table_analysis())

        elif choice == "4":
            print("\nGenerating master analytics dashboard...")
            visualizer.plot_unified_dashboard()

        elif choice == "5":
            print("\nGenerating attendance vs performance plot...")
            visualizer.plot_attendance_vs_performance_bubble()

        elif choice == "6":
            out_file = "data/processed_payroll_records.csv"
            df.to_csv(out_file, index=False)
            print(f"\nSuccessfully exported {len(df)} records to '{out_file}'.")

        elif choice == "7":
            print("\nExiting system. Pipeline terminated.")
            break

        else:
            print("Invalid input. Please choose an option between 1 and 7.")

if __name__ == "__main__":
    main()