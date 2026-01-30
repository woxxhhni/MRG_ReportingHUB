"""
Example usage of MRGDate and date utilities.
Run from project root: python examples/date_example.py
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import pandas as pd
import datetime
from utils import MRGDate, convert_dataframe_dates, date_range, business_days_between

# Example 1: Create date from various sources
print("=" * 60)
print("Example 1: Create dates from various sources")
print("=" * 60)

# From integers
date1 = MRGDate(15, 1, 2024)  # January 15, 2024
print(f"From integers: {date1}")

# From string
date2 = MRGDate.from_string('2024-06-30', '%Y-%m-%d')
print(f"From string: {date2}")

# From datetime
dt = datetime.datetime(2024, 3, 15, 14, 30, 0)
date3 = MRGDate.from_datetime(dt)
print(f"From datetime: {date3}")

# From pandas Timestamp
ts = pd.Timestamp('2024-12-25')
date4 = MRGDate.from_pandas(ts)
print(f"From pandas Timestamp: {date4}")

# From string (auto-detect format)
date5 = MRGDate.from_pandas('2024-01-15')
print(f"From string (auto-detect): {date5}")

# Example 2: Date operations
print("\n" + "=" * 60)
print("Example 2: Date operations")
print("=" * 60)

date6 = date1.add_days(30)
print(f"Date 1 + 30 days: {date6}")

date7 = date1.add_months(3)
print(f"Date 1 + 3 months: {date7}")

date8 = date1.add_years(1)
print(f"Date 1 + 1 year: {date8}")

# Example 3: Weekday operations
print("\n" + "=" * 60)
print("Example 3: Weekday operations")
print("=" * 60)

print(f"Is {date1} weekend? {date1.is_weekend()}")
print(f"Weekday: {date1.weekday} (0=Monday, 6=Sunday)")

date9 = date1.add_weekdays(5)  # Add 5 weekdays
print(f"Date 1 + 5 weekdays: {date9}")

# Example 4: Date comparison
print("\n" + "=" * 60)
print("Example 4: Date comparison")
print("=" * 60)

print(f"Date 1 < Date 2: {date1 < date2}")
print(f"Date 1 > Date 2: {date1 > date2}")
print(f"Days difference: {date2 - date1}")

# Example 5: Format dates
print("\n" + "=" * 60)
print("Example 5: Format dates")
print("=" * 60)

print(f"Default format: {date1}")
print(f"Custom format: {date1.to_string('%d/%m/%Y')}")
print(f"ISO format: {date1.to_string('%Y-%m-%d')}")

# Example 6: Access properties
print("\n" + "=" * 60)
print("Example 6: Access properties")
print("=" * 60)

print(f"Day: {date1.day}")
print(f"Month: {date1.month}")
print(f"Year: {date1.year}")
print(f"Weekday: {date1.weekday}")

# Example 7: Useful date functions
print("\n" + "=" * 60)
print("Example 7: Useful date functions")
print("=" * 60)

print(f"Start of month: {date1.start_of_month()}")
print(f"End of month: {date1.end_of_month()}")
print(f"Start of quarter: {date1.start_of_quarter()}")
print(f"End of quarter: {date1.end_of_quarter()}")
print(f"Start of year: {date1.start_of_year()}")
print(f"End of year: {date1.end_of_year()}")
print(f"Quarter: Q{date1.quarter()}")
print(f"Days in month: {date1.days_in_month()}")
print(f"Days in year: {date1.days_in_year()}")
print(f"Is month end: {date1.is_month_end()}")
print(f"Is quarter end: {date1.is_quarter_end()}")
print(f"Is year end: {date1.is_year_end()}")

# Example 8: Business day operations
print("\n" + "=" * 60)
print("Example 8: Business day operations")
print("=" * 60)

print(f"Next business day: {date1.next_business_day()}")
print(f"Previous business day: {date1.previous_business_day()}")

# Example 9: Date calculations
print("\n" + "=" * 60)
print("Example 9: Date calculations")
print("=" * 60)

print(f"Days between date1 and date2: {date1.days_between(date2)}")
print(f"Months between: {date1.months_between(date2):.2f}")
print(f"Years between: {date1.years_between(date2):.2f}")

# Example 10: DataFrame operations
print("\n" + "=" * 60)
print("Example 10: DataFrame operations")
print("=" * 60)

# Create sample DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3],
    'date': ['2024-01-15', '2024-02-20', '2024-03-25'],
    'value': [100, 200, 300]
})

print("Original DataFrame:")
print(df)
print(f"\nDate column type: {df['date'].dtype}")

# Convert date column to MRGDate
df_converted = convert_dataframe_dates(df, 'date')
print("\nAfter conversion:")
print(df_converted)
print(f"Date column type: {type(df_converted['date'].iloc[0])}")

# Example 11: Date range generation
print("\n" + "=" * 60)
print("Example 11: Date range generation")
print("=" * 60)

dates = date_range('2024-01-01', '2024-01-10', step_days=2)
print(f"Date range (every 2 days): {[str(d) for d in dates]}")

# Example 12: Business days calculation
print("\n" + "=" * 60)
print("Example 12: Business days calculation")
print("=" * 60)

bd_count = business_days_between('2024-01-01', '2024-01-31')
print(f"Business days between Jan 1 and Jan 31: {bd_count}")

print("\n" + "=" * 60)
print("All examples completed!")
print("=" * 60)
