"""
Example usage of DBManager for MAVRICK DB
"""

from pathlib import Path
import pandas as pd
from utils import DBManager, create_mavrick_db_manager

# ============================================================================
# Example 1: Create DB manager using factory function with default settings
# ============================================================================
print("=" * 60)
print("Example 1: Connect to MAVRICK DB with default settings")
print("=" * 60)

db = create_mavrick_db_manager()
print(f"Connected to: {db.server}/{db.database}\n")

# ============================================================================
# Example 2: Run query from string
# ============================================================================
print("=" * 60)
print("Example 2: Execute query from string")
print("=" * 60)

query = "SELECT TOP 10 * FROM MAV2.UIUMissingData"
df = db.run_query_from_string(query)
print(f"Retrieved {len(df)} rows")
print(f"Columns: {list(df.columns)}\n")
print(df.head())

# ============================================================================
# Example 3: Run query from file
# ============================================================================
print("\n" + "=" * 60)
print("Example 3: Execute query from SQL file")
print("=" * 60)

sql_file = Path("queries/uiu_missing_data.sql")
df_from_file = db.run_query_from_file(sql_file)
print(f"Retrieved {len(df_from_file)} rows from file\n")

# ============================================================================
# Example 4: Save query result to interim data folder
# ============================================================================
print("=" * 60)
print("Example 4: Save query result to interim data")
print("=" * 60)

# Save as CSV
output_csv = Path("interim_data/uiu_missing_data.csv")
df_from_file.to_csv(output_csv, index=False)
print(f"Saved to CSV: {output_csv}")

# Save as Parquet (more efficient for large datasets)
output_parquet = Path("interim_data/uiu_missing_data.parquet")
df_from_file.to_parquet(output_parquet, index=False)
print(f"Saved to Parquet: {output_parquet}\n")

# ============================================================================
# Example 5: Load interim data for reporting
# ============================================================================
print("=" * 60)
print("Example 5: Load interim data for reporting")
print("=" * 60)

# Load from CSV
df_loaded = pd.read_csv(output_csv)
print(f"Loaded {len(df_loaded)} rows from CSV")

# Or load from Parquet
df_loaded_parquet = pd.read_parquet(output_parquet)
print(f"Loaded {len(df_loaded_parquet)} rows from Parquet\n")

# ============================================================================
# Example 6: Parameterized query
# ============================================================================
print("=" * 60)
print("Example 6: Parameterized query")
print("=" * 60)

query_with_params = """
    SELECT TOP :limit_rows *
    FROM MAV2.UIUMissingData
    WHERE SomeDateColumn >= :start_date
"""

# Note: SQL Server uses :param_name for parameters in SQLAlchemy
df_param = db.run_query_from_string(
    query_with_params,
    params={"limit_rows": 5, "start_date": "2024-01-01"}
)
print(f"Retrieved {len(df_param)} rows with parameters\n")

# Example 6b: Custom placeholders (e.g., (0=0), (1=1))
print("=" * 60)
print("Example 6b: Query with custom placeholders")
print("=" * 60)

query_with_placeholders = """
    SELECT * FROM your_table
    WHERE (0=0) AND (1=1)
"""

# Replace placeholders with actual conditions
df_placeholder = db.run_query_from_string(
    query_with_placeholders,
    placeholders={
        "(0=0)": "(status = 'active')",  # Replace (0=0) with actual condition
        "(1=1)": "(deleted = 0)"         # Replace (1=1) with actual condition
    }
)
print(f"Retrieved {len(df_placeholder)} rows with placeholders\n")

# Example 6c: Using both parameterized queries and placeholders
print("=" * 60)
print("Example 6c: Combining placeholders and parameters")
print("=" * 60)

query_combined = """
    SELECT * FROM your_table
    WHERE (0=0) AND id = :id AND date >= :start_date
"""

df_combined = db.run_query_from_string(
    query_combined,
    params={"id": 123, "start_date": "2024-01-01"},
    placeholders={"(0=0)": "(status = 'active')"}
)
print(f"Retrieved {len(df_combined)} rows with both placeholders and parameters\n")

# ============================================================================
# Example 7: Insert DataFrame into database table
# ============================================================================
print("=" * 60)
print("Example 7: Insert DataFrame into database")
print("=" * 60)

# Example: Create a sample DataFrame
sample_data = pd.DataFrame({
    "id": [1, 2, 3],
    "name": ["Test1", "Test2", "Test3"],
    "value": [100.5, 200.3, 300.7]
})

# Uncomment to actually insert (be careful!)
# rows_inserted = db.insert_dataframe(
#     df=sample_data,
#     table_name="YourTableName",
#     schema="MAV2",
#     if_exists="append"
# )
# print(f"Inserted {rows_inserted} rows\n")

# ============================================================================
# Example 8: Using context manager (automatic connection cleanup)
# ============================================================================
print("=" * 60)
print("Example 8: Using context manager")
print("=" * 60)

with create_mavrick_db_manager() as db_ctx:
    df_ctx = db_ctx.run_query_from_string("SELECT TOP 5 * FROM MAV2.UIUMissingData")
    print(f"Retrieved {len(df_ctx)} rows")
    # Connection automatically closed when exiting context
print("Connection closed automatically\n")

# ============================================================================
# Example 9: Test connection
# ============================================================================
print("=" * 60)
print("Example 9: Test connection")
print("=" * 60)

is_connected = db.test_connection()
print(f"Connection status: {'Connected' if is_connected else 'Failed'}\n")

# ============================================================================
# Cleanup: Close connection
# ============================================================================
db.close()
print("Database connection closed")
