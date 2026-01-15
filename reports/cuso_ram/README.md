# CUSO RAM Report

## Overview

CUSO RAM (Risk Appetite Measure) Report processes and aggregates model information from the Model Governance team.

## Query

- **Query File**: `queries/Risk Appetite Measure.sql`
- **Purpose**: Download all models information from Model Governance team

## Report Structure

The report generates an Excel file with multiple sheets:

1. **Overall_Summary** - High-level statistics
2. **Summary_by_Owner** - Aggregated data by model owner
3. **Summary_by_Type** - Aggregated data by model type (if applicable)
4. **Detail** - Complete detailed data

## Usage

```python
from reports.cuso_ram_report import CUSORAMReport

# Create and run report
report = CUSORAMReport()
report_path = report.run()
```

## Output

- **Excel Report**: `output_data/cuso_ram/CUSO_RAM_Report_YYYYMMDD_HHMMSS.xlsx`
- **Interim Data**: `interim_data/cuso_ram/cuso_ram_data_YYYYMMDD.csv` and `.parquet`

## Data Processing

1. Extract data from MAVRICK database using the query
2. Clean and transform the data
3. Calculate aggregations by:
   - Model Owner
   - Model Type (if applicable)
   - Other dimensions as needed
4. Generate Excel report with multiple sheets
5. Save interim data for future use

## Notes

- Update the SQL query with actual table names and schema
- Adjust aggregation logic based on actual data structure
- Modify column names in `calculate_aggregations()` to match your data
