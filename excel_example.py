"""
Example usage of ExcelManager
"""

import pandas as pd
from pathlib import Path
from utils import ExcelManager

# Initialize Excel Manager
excel_mgr = ExcelManager(output_dir="output_data")

# ============================================================================
# Example 1: Save a single DataFrame to Excel
# ============================================================================
print("=" * 60)
print("Example 1: Save single DataFrame to Excel")
print("=" * 60)

df1 = pd.DataFrame({
    "ID": [1, 2, 3, 4, 5],
    "Name": ["Alice", "Bob", "Charlie", "David", "Eve"],
    "Value": [100.5, 200.3, 150.7, 300.2, 250.9],
    "Date": pd.date_range("2024-01-01", periods=5)
})

# Method 1: Using default position (A1)
excel_path = excel_mgr.save_dataframe(
    df=df1,
    file_path="output_data/example_single.xlsx",
    sheet_name="Data",
    index=False
)
print(f"Saved to: {excel_path} (default position A1)")

# Method 2: Using Excel cell reference
excel_path2 = excel_mgr.save_dataframe(
    df=df1,
    file_path="output_data/example_single_cellref.xlsx",
    sheet_name="Data",
    start_cell="B3",  # Start at cell B3
    index=False
)
print(f"Saved to: {excel_path2} (starting at B3)\n")

# ============================================================================
# Example 2: Save multiple DataFrames to one Excel file (multiple sheets)
# ============================================================================
print("=" * 60)
print("Example 2: Save multiple DataFrames to one Excel file")
print("=" * 60)

# Create multiple DataFrames
df_summary = pd.DataFrame({
    "Metric": ["Total", "Average", "Max", "Min"],
    "Value": [1000, 200, 500, 50]
})

df_detail = pd.DataFrame({
    "ID": range(1, 11),
    "Item": [f"Item_{i}" for i in range(1, 11)],
    "Amount": [i * 10.5 for i in range(1, 11)]
})

df_trends = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
    "Sales": [100, 120, 150, 130, 160],
    "Growth": [0, 20, 25, -13, 23]
})

# Save all to one Excel file
dataframes = {
    "Summary": df_summary,
    "Detail": df_detail,
    "Trends": df_trends
}

excel_path = excel_mgr.save_multiple_dataframes(
    dataframes=dataframes,
    file_path="output_data/example_multiple_sheets.xlsx"
)
print(f"Saved to: {excel_path}\n")

# ============================================================================
# Example 3: Append DataFrame to existing Excel file
# ============================================================================
print("=" * 60)
print("Example 3: Append DataFrame to existing Excel")
print("=" * 60)

# Create new data to append
df_new = pd.DataFrame({
    "ID": [6, 7, 8],
    "Name": ["Frank", "Grace", "Henry"],
    "Value": [180.5, 220.3, 190.7],
    "Date": pd.date_range("2024-01-06", periods=3)
})

# Method 1: Append to end (default)
excel_path = excel_mgr.append_dataframe(
    df=df_new,
    file_path="output_data/example_single.xlsx",
    sheet_name="Data"
)
print(f"Appended to: {excel_path} (end of sheet)")

# Method 2: Append at specific cell position
excel_path2 = excel_mgr.append_dataframe(
    df=df_new,
    file_path="output_data/example_single_cellref.xlsx",
    sheet_name="Data",
    start_cell="A10"  # Start appending at cell A10
)
print(f"Appended to: {excel_path2} (starting at A10)\n")

# ============================================================================
# Example 4: Read Excel file
# ============================================================================
print("=" * 60)
print("Example 4: Read Excel file")
print("=" * 60)

# Read specific sheet
df_read = excel_mgr.read_excel(
    file_path="output_data/example_multiple_sheets.xlsx",
    sheet_name="Summary"
)
print(f"Read Summary sheet: {len(df_read)} rows")
print(df_read.head())

# Read all sheets
all_sheets = excel_mgr.read_excel(
    file_path="output_data/example_multiple_sheets.xlsx"
)
print(f"\nAll sheets: {list(all_sheets.keys())}")

# ============================================================================
# Example 5: List sheets in Excel file
# ============================================================================
print("\n" + "=" * 60)
print("Example 5: List sheets in Excel file")
print("=" * 60)

sheet_names = excel_mgr.list_sheets("output_data/example_multiple_sheets.xlsx")
print(f"Sheet names: {sheet_names}")

# ============================================================================
# Example 6: Integration with DB Manager
# ============================================================================
print("\n" + "=" * 60)
print("Example 6: Integration with DB Manager")
print("=" * 60)

# This shows how you might use Excel Manager with DB Manager
# from utils import create_mavrick_db_manager
# 
# db = create_mavrick_db_manager()
# df_from_db = db.run_query_from_string("SELECT * FROM MAV2.UIUMissingData")
# 
# # Save query result to Excel
# excel_mgr.save_dataframe(
#     df=df_from_db,
#     file_path="output_data/uiu_missing_data.xlsx",
#     sheet_name="UIU Missing Data"
# )

print("Example completed!")
