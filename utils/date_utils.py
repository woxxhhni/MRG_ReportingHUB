"""
Date Utilities
Date class and utilities for MRG Reporting HUB
Based on VVTDate from KPMG Advisory(China) LTD. FRM
"""

import datetime
import pandas as pd
from typing import Optional, Union, List


class DateError(Exception):
    """Custom exception for date-related errors."""
    pass


# Days per month for non-leap years
MONTH_DAYS_NOT_LEAP_YEAR = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
# Days per month for leap years
MONTH_DAYS_LEAP_YEAR = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def is_leap_year(year: int) -> bool:
    """
    Check if a year is a leap year.
    
    Args:
        year: Year to check
        
    Returns:
        True if leap year, False otherwise
    """
    return ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0)


def parse_date(date_str: str, date_format: str) -> tuple:
    """
    Parse date string into day, month, year.
    
    Args:
        date_str: Date string
        date_format: Date format string
        
    Returns:
        Tuple of (day, month, year)
    """
    dt_obj = datetime.datetime.strptime(date_str, date_format)
    return dt_obj.day, dt_obj.month, dt_obj.year


# Date counter for Excel date calculations (internal use only)
_g_date_counter_list = None
_g_start_year = 1900
_g_end_year = 2100


def _calculate_date_list():
    """Calculate date counter list for Excel date compatibility (internal use)."""
    global _g_date_counter_list, _g_start_year, _g_end_year
    
    day_counter = 0
    max_days = 0
    _g_date_counter_list = []
    
    idx = -1
    
    for yy in range(_g_start_year, _g_end_year + 1):
        # Excel compatibility: 1900 is treated as leap year
        if yy == 1900:
            leap_year = True
        else:
            leap_year = is_leap_year(yy)
        
        for mm in range(1, 13):
            if leap_year:
                max_days = MONTH_DAYS_LEAP_YEAR[mm - 1]
            else:
                max_days = MONTH_DAYS_NOT_LEAP_YEAR[mm - 1]
            
            for _ in range(1, max_days + 1):
                idx += 1
                day_counter += 1
                if yy >= _g_start_year:
                    _g_date_counter_list.append(day_counter)
            
            for _ in range(max_days, 31):
                idx += 1
                if yy >= _g_start_year:
                    _g_date_counter_list.append(-999)


def _date_index(day: int, month: int, year: int) -> int:
    """Get index in date counter list (internal use)."""
    return (year - _g_start_year) * 12 * 31 + (month - 1) * 31 + (day - 1)


def _date_from_index(idx: int) -> tuple:
    """Get date (day, month, year) from index (internal use)."""
    year = int(_g_start_year + idx / 12 / 31)
    month = 1 + int((idx - (year - _g_start_year) * 12 * 31) / 31)
    day = 1 + idx - (year - _g_start_year) * 12 * 31 - (month - 1) * 31
    return (day, month, year)


def _weekday(day_count: int) -> int:
    """Get weekday from day count (Monday = 0) (internal use)."""
    return (day_count + 5) % 7


class MRGDate:
    """
    Date class for MRG Reporting HUB.
    Provides date operations and calculations.
    
    Example:
        # Create date
        date1 = MRGDate(15, 1, 2024)  # January 15, 2024
        
        # From string
        date2 = MRGDate.from_string('2024-01-15', '%Y-%m-%d')
        
        # Add days
        date3 = date1.add_days(30)
        
        # Check if weekend
        is_weekend = date1.is_weekend()
    """
    
    # Weekday constants
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6
    
    def __init__(self,
                 day: int,
                 month: int,
                 year: int,
                 hour: int = 0,
                 minute: int = 0,
                 second: int = 0):
        """
        Initialize date.
        
        Args:
            day: Day (1-31)
            month: Month (1-12)
            year: Year
            hour: Hour (0-23), default 0
            minute: Minute (0-59), default 0
            second: Second (0-59), default 0
        """
        global _g_date_counter_list, _g_start_year, _g_end_year
        
        # Initialize date counter list if needed
        if _g_date_counter_list is None:
            _calculate_date_list()
        
        # Adjust year range if needed
        if year < _g_start_year:
            _g_start_year = year
            _calculate_date_list()
        
        if year > _g_end_year:
            _g_end_year = year
            _calculate_date_list()
        
        if year < _g_start_year or year > _g_end_year:
            raise DateError(
                f"Year {year} should be between {_g_start_year} and {_g_end_year}"
            )
        
        if day < 1:
            raise DateError("Day must be greater than 0")
        
        leap_year = is_leap_year(year)
        
        if leap_year:
            if day > MONTH_DAYS_LEAP_YEAR[month - 1]:
                raise DateError(f"Invalid day {day} for month {month} in leap year {year}")
        else:
            if day > MONTH_DAYS_NOT_LEAP_YEAR[month - 1]:
                raise DateError(f"Invalid day {day} for month {month} in year {year}")
        
        if hour < 0 or hour > 23:
            raise DateError("Hour must be between 0-23")
        
        if minute < 0 or minute > 59:
            raise DateError("Minute must be between 0-59")
        
        if second < 0 or second > 59:
            raise DateError("Second must be between 0-59")
        
        self._year = year
        self._month = month
        self._day = day
        self._hour = hour
        self._minute = minute
        self._second = second
        
        self._excel_date = 0.0
        
        # Refresh date calculations
        self._refresh()
        
        # Add time fraction
        day_fraction = self._hour / 24.0
        day_fraction += self._minute / 24.0 / 60.0
        day_fraction += self._second / 24.0 / 60.0 / 60.0
        
        self._excel_date += day_fraction
    
    @classmethod
    def from_string(cls, date_string: str, format_string: str):
        """
        Create date from string.
        
        Args:
            date_string: Date string
            format_string: Date format string
            
        Returns:
            MRGDate instance
            
        Examples:
            # ISO format
            date = MRGDate.from_string('2024-01-15', '%Y-%m-%d')
            
            # US format
            date = MRGDate.from_string('01/15/2024', '%m/%d/%Y')
            
            # UK format
            date = MRGDate.from_string('15/01/2024', '%d/%m/%Y')
            
            # Compact format
            date = MRGDate.from_string('20240115', '%Y%m%d')
            
            # With time
            date = MRGDate.from_string('2024-01-15 14:30:00', '%Y-%m-%d %H:%M:%S')
            
            # Common format strings:
            # '%Y-%m-%d'      -> 2024-01-15
            # '%Y/%m/%d'      -> 2024/01/15
            # '%d-%m-%Y'      -> 15-01-2024
            # '%d/%m/%Y'      -> 15/01/2024
            # '%m/%d/%Y'      -> 01/15/2024
            # '%Y%m%d'        -> 20240115
            # '%Y-%m-%d %H:%M:%S' -> 2024-01-15 14:30:00
        """
        day, month, year = parse_date(date_string, format_string)
        return cls(day, month, year)
    
    @classmethod
    def from_datetime(cls, dt: Union[datetime.datetime, datetime.date]):
        """
        Create date from datetime or date object.
        
        Args:
            dt: datetime.datetime or datetime.date object
            
        Returns:
            MRGDate instance
        """
        if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
            return cls(dt.day, dt.month, dt.year)
        return cls(dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second)
    
    @classmethod
    def from_pandas(cls, value: Union[pd.Timestamp, str, datetime.datetime, datetime.date]):
        """
        Create date from pandas Timestamp or other common types.
        
        Args:
            value: pandas Timestamp, string, datetime, or date
            
        Returns:
            MRGDate instance
        """
        if isinstance(value, pd.Timestamp):
            return cls(value.day, value.month, value.year, value.hour, value.minute, value.second)
        elif isinstance(value, (datetime.datetime, datetime.date)):
            return cls.from_datetime(value)
        elif isinstance(value, str):
            # Try common formats
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%Y%m%d']:
                try:
                    return cls.from_string(value, fmt)
                except ValueError:
                    continue
            raise DateError(f"Unable to parse date string: {value}")
        else:
            raise DateError(f"Unsupported type: {type(value)}")
    
    @classmethod
    def from_dataframe_column(cls, df: pd.DataFrame, column_name: str) -> List['MRGDate']:
        """
        Convert DataFrame column to list of MRGDate objects.
        
        Args:
            df: pandas DataFrame
            column_name: Name of the date column
            
        Returns:
            List of MRGDate objects
        """
        if column_name not in df.columns:
            raise DateError(f"Column '{column_name}' not found in DataFrame")
        
        dates = []
        for value in df[column_name]:
            if pd.isna(value):
                dates.append(None)
            else:
                dates.append(cls.from_pandas(value))
        
        return dates
    
    def _refresh(self):
        """Refresh date calculations."""
        idx = _date_index(self._day, self._month, self._year)
        days_since_1900 = _g_date_counter_list[idx]
        weekday = _weekday(days_since_1900)
        self._excel_date = days_since_1900
        self._weekday = weekday
    
    # Comparison operators
    def __lt__(self, other):
        """Less than comparison."""
        return self._excel_date < other._excel_date
    
    def __gt__(self, other):
        """Greater than comparison."""
        return self._excel_date > other._excel_date
    
    def __le__(self, other):
        """Less than or equal comparison."""
        return self._excel_date <= other._excel_date
    
    def __ge__(self, other):
        """Greater than or equal comparison."""
        return self._excel_date >= other._excel_date
    
    def __eq__(self, other):
        """Equality comparison."""
        return self._excel_date == other._excel_date
    
    def __sub__(self, other):
        """Subtract two dates (returns days difference)."""
        return self._excel_date - other._excel_date
    
    def is_weekend(self) -> bool:
        """
        Check if date is weekend.
        
        Returns:
            True if weekend, False otherwise
        """
        return self._weekday == MRGDate.SAT or self._weekday == MRGDate.SUN
    
    def add_days(self, num_days: int):
        """
        Add days to date.
        
        Args:
            num_days: Number of days to add (can be negative)
            
        Returns:
            New MRGDate instance
        """
        idx = _date_index(self._day, self._month, self._year)
        
        step = 1 if num_days >= 0 else -1
        
        while num_days != 0:
            idx += step
            if _g_date_counter_list[idx] > 0:
                num_days -= step
        
        day, month, year = _date_from_index(idx)
        return MRGDate(day, month, year, self._hour, self._minute, self._second)
    
    def add_weekdays(self, num_days: int):
        """
        Add weekdays (excluding weekends) to date.
        
        Args:
            num_days: Number of weekdays to add
            
        Returns:
            New MRGDate instance
        """
        if not isinstance(num_days, int):
            raise DateError("Number of days must be an integer")
        
        dt = datetime.date(self._year, self._month, self._day)
        new_dt = MRGDate(dt.day, dt.month, dt.year)
        
        step = 1 if num_days >= 0 else -1
        if num_days < 0:
            num_days = -num_days
        
        while num_days > 0:
            dt = dt + step * datetime.timedelta(days=1)
            new_dt = MRGDate(dt.day, dt.month, dt.year)
            
            if not new_dt.is_weekend():
                num_days -= 1
        
        return new_dt
    
    def add_months(self, num_months: int):
        """
        Add months to date.
        
        Args:
            num_months: Number of months to add (can be negative)
            
        Returns:
            New MRGDate instance
        """
        day = self._day
        month = self._month + num_months
        year = self._year
        
        while month > 12:
            month -= 12
            year += 1
        
        while month < 1:
            month += 12
            year -= 1
        
        leap_year = is_leap_year(year)
        
        if leap_year:
            if day > MONTH_DAYS_LEAP_YEAR[month - 1]:
                day = MONTH_DAYS_LEAP_YEAR[month - 1]
        else:
            if day > MONTH_DAYS_NOT_LEAP_YEAR[month - 1]:
                day = MONTH_DAYS_NOT_LEAP_YEAR[month - 1]
        
        return MRGDate(day, month, year, self._hour, self._minute, self._second)
    
    def add_years(self, num_years: int):
        """
        Add years to date.
        
        Args:
            num_years: Number of years to add (can be negative)
            
        Returns:
            New MRGDate instance
        """
        new_date = self.add_months(num_years * 12)
        return new_date
    
    def start_of_month(self):
        """
        Get first day of the month.
        
        Returns:
            New MRGDate instance for the first day of the month
        """
        return MRGDate(1, self._month, self._year)
    
    def end_of_month(self):
        """
        Get last day of the month.
        
        Returns:
            New MRGDate instance for the last day of the month
        """
        leap_year = is_leap_year(self._year)
        if leap_year:
            last_day = MONTH_DAYS_LEAP_YEAR[self._month - 1]
        else:
            last_day = MONTH_DAYS_NOT_LEAP_YEAR[self._month - 1]
        return MRGDate(last_day, self._month, self._year)
    
    def start_of_quarter(self):
        """
        Get first day of the quarter.
        
        Returns:
            New MRGDate instance for the first day of the quarter
        """
        quarter_month = ((self._month - 1) // 3) * 3 + 1
        return MRGDate(1, quarter_month, self._year)
    
    def end_of_quarter(self):
        """
        Get last day of the quarter.
        
        Returns:
            New MRGDate instance for the last day of the quarter
        """
        quarter_month = ((self._month - 1) // 3 + 1) * 3
        leap_year = is_leap_year(self._year)
        if leap_year:
            last_day = MONTH_DAYS_LEAP_YEAR[quarter_month - 1]
        else:
            last_day = MONTH_DAYS_NOT_LEAP_YEAR[quarter_month - 1]
        return MRGDate(last_day, quarter_month, self._year)
    
    def start_of_year(self):
        """
        Get first day of the year.
        
        Returns:
            New MRGDate instance for January 1st
        """
        return MRGDate(1, 1, self._year)
    
    def end_of_year(self):
        """
        Get last day of the year.
        
        Returns:
            New MRGDate instance for December 31st
        """
        return MRGDate(31, 12, self._year)
    
    def quarter(self) -> int:
        """
        Get quarter number (1-4).
        
        Returns:
            Quarter number
        """
        return (self._month - 1) // 3 + 1
    
    def days_in_month(self) -> int:
        """
        Get number of days in the month.
        
        Returns:
            Number of days in the month
        """
        leap_year = is_leap_year(self._year)
        if leap_year:
            return MONTH_DAYS_LEAP_YEAR[self._month - 1]
        else:
            return MONTH_DAYS_NOT_LEAP_YEAR[self._month - 1]
    
    def days_in_year(self) -> int:
        """
        Get number of days in the year.
        
        Returns:
            365 or 366
        """
        return 366 if is_leap_year(self._year) else 365
    
    def is_month_end(self) -> bool:
        """
        Check if date is the last day of the month.
        
        Returns:
            True if last day of month, False otherwise
        """
        return self._day == self.days_in_month()
    
    def is_quarter_end(self) -> bool:
        """
        Check if date is the last day of the quarter.
        
        Returns:
            True if last day of quarter, False otherwise
        """
        return self == self.end_of_quarter()
    
    def is_year_end(self) -> bool:
        """
        Check if date is the last day of the year.
        
        Returns:
            True if December 31st, False otherwise
        """
        return self._month == 12 and self._day == 31
    
    def next_business_day(self):
        """
        Get next business day (skipping weekends).
        
        Returns:
            New MRGDate instance for next business day
        """
        next_date = self.add_days(1)
        while next_date.is_weekend():
            next_date = next_date.add_days(1)
        return next_date
    
    def previous_business_day(self):
        """
        Get previous business day (skipping weekends).
        
        Returns:
            New MRGDate instance for previous business day
        """
        prev_date = self.add_days(-1)
        while prev_date.is_weekend():
            prev_date = prev_date.add_days(-1)
        return prev_date
    
    def days_between(self, other: 'MRGDate') -> int:
        """
        Calculate number of days between two dates.
        
        Args:
            other: Another MRGDate instance
            
        Returns:
            Number of days (can be negative)
        """
        return int(other._excel_date - self._excel_date)
    
    def months_between(self, other: 'MRGDate') -> float:
        """
        Calculate approximate number of months between two dates.
        
        Args:
            other: Another MRGDate instance
            
        Returns:
            Approximate number of months
        """
        days_diff = self.days_between(other)
        return days_diff / 30.44  # Average days per month
    
    def years_between(self, other: 'MRGDate') -> float:
        """
        Calculate approximate number of years between two dates.
        
        Args:
            other: Another MRGDate instance
            
        Returns:
            Approximate number of years
        """
        days_diff = self.days_between(other)
        return days_diff / 365.25  # Average days per year
    
    def age_in_days(self, reference_date: Optional['MRGDate'] = None) -> int:
        """
        Calculate age in days from reference date (default: today).
        
        Args:
            reference_date: Reference date (default: today)
            
        Returns:
            Age in days
        """
        if reference_date is None:
            today = datetime.date.today()
            reference_date = MRGDate(today.day, today.month, today.year)
        return abs(self.days_between(reference_date))
    
    def is_same_month(self, other: 'MRGDate') -> bool:
        """
        Check if two dates are in the same month.
        
        Args:
            other: Another MRGDate instance
            
        Returns:
            True if same month and year, False otherwise
        """
        return self._year == other._year and self._month == other._month
    
    def is_same_quarter(self, other: 'MRGDate') -> bool:
        """
        Check if two dates are in the same quarter.
        
        Args:
            other: Another MRGDate instance
            
        Returns:
            True if same quarter and year, False otherwise
        """
        return self._year == other._year and self.quarter() == other.quarter()
    
    def is_same_year(self, other: 'MRGDate') -> bool:
        """
        Check if two dates are in the same year.
        
        Args:
            other: Another MRGDate instance
            
        Returns:
            True if same year, False otherwise
        """
        return self._year == other._year
    
    def to_datetime(self) -> datetime.date:
        """
        Convert to datetime.date object.
        
        Returns:
            datetime.date object
        """
        return datetime.date(self._year, self._month, self._day)
    
    def to_string(self, format_string: str = '%Y-%m-%d') -> str:
        """
        Convert to string.
        
        Args:
            format_string: Format string (default: '%Y-%m-%d')
            
        Returns:
            Formatted date string
            
        Examples:
            date = MRGDate(15, 1, 2024)  # January 15, 2024
            
            # ISO format
            date.to_string('%Y-%m-%d')           # '2024-01-15'
            
            # US format
            date.to_string('%m/%d/%Y')           # '01/15/2024'
            
            # UK format
            date.to_string('%d/%m/%Y')           # '15/01/2024'
            
            # Compact format
            date.to_string('%Y%m%d')             # '20240115'
            
            # With time
            date.to_string('%Y-%m-%d %H:%M:%S')  # '2024-01-15 14:30:00'
            
            # Common format strings:
            # '%Y-%m-%d'      -> 2024-01-15
            # '%Y/%m/%d'      -> 2024/01/15
            # '%d-%m-%Y'      -> 15-01-2024
            # '%d/%m/%Y'      -> 15/01/2024
            # '%m/%d/%Y'      -> 01/15/2024
            # '%Y%m%d'        -> 20240115
            # '%Y-%m-%d %H:%M:%S' -> 2024-01-15 14:30:00
            # '%d %B %Y'      -> 15 January 2024
            # '%B %d, %Y'     -> January 15, 2024
        """
        dt = datetime.datetime(self._year, self._month, self._day,
                              self._hour, self._minute, self._second)
        return dt.strftime(format_string)
    
    def __repr__(self):
        """String representation."""
        return f"MRGDate({self._day}, {self._month}, {self._year})"
    
    def __str__(self):
        """String representation."""
        return self.to_string('%Y-%m-%d')
    
    @property
    def day(self) -> int:
        """Get day."""
        return self._day
    
    @property
    def month(self) -> int:
        """Get month."""
        return self._month
    
    @property
    def year(self) -> int:
        """Get year."""
        return self._year
    
    @property
    def weekday(self) -> int:
        """Get weekday (Monday = 0)."""
        return self._weekday


# Utility functions (defined after MRGDate class)
def convert_dataframe_dates(df: pd.DataFrame, 
                            date_columns: Union[str, List[str]],
                            inplace: bool = False) -> Optional[pd.DataFrame]:
    """
    Convert DataFrame date columns to MRGDate objects.
    
    Args:
        df: pandas DataFrame
        date_columns: Column name(s) to convert
        inplace: If True, modify DataFrame in place
        
    Returns:
        DataFrame with converted dates (if inplace=False), None if inplace=True
        
    Example:
        # Convert single column
        df = convert_dataframe_dates(df, 'date_column')
        
        # Convert multiple columns
        df = convert_dataframe_dates(df, ['start_date', 'end_date'])
        
        # In place conversion
        convert_dataframe_dates(df, 'date_column', inplace=True)
    """
    if not inplace:
        df = df.copy()
    
    if isinstance(date_columns, str):
        date_columns = [date_columns]
    
    for col in date_columns:
        if col not in df.columns:
            raise DateError(f"Column '{col}' not found in DataFrame")
        
        df[col] = df[col].apply(
            lambda x: MRGDate.from_pandas(x) if pd.notna(x) else None
        )
    
    return None if inplace else df


def date_range(start_date: Union[MRGDate, str, datetime.date],
               end_date: Union[MRGDate, str, datetime.date],
               step_days: int = 1) -> List[MRGDate]:
    """
    Generate a list of dates between start and end dates.
    
    Args:
        start_date: Start date (MRGDate, string, or datetime)
        end_date: End date (MRGDate, string, or datetime)
        step_days: Step size in days (default: 1)
        
    Returns:
        List of MRGDate objects
        
    Example:
        dates = date_range('2024-01-01', '2024-01-31', step_days=7)
    """
    if not isinstance(start_date, MRGDate):
        start_date = MRGDate.from_pandas(start_date)
    if not isinstance(end_date, MRGDate):
        end_date = MRGDate.from_pandas(end_date)
    
    dates = []
    current = start_date
    
    if start_date <= end_date:
        while current <= end_date:
            dates.append(current)
            current = current.add_days(step_days)
    else:
        while current >= end_date:
            dates.append(current)
            current = current.add_days(-step_days)
    
    return dates


def business_days_between(start_date: Union[MRGDate, str, datetime.date],
                          end_date: Union[MRGDate, str, datetime.date]) -> int:
    """
    Calculate number of business days between two dates (excluding weekends).
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Number of business days
    """
    if not isinstance(start_date, MRGDate):
        start_date = MRGDate.from_pandas(start_date)
    if not isinstance(end_date, MRGDate):
        end_date = MRGDate.from_pandas(end_date)
    
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    count = 0
    current = start_date
    
    while current <= end_date:
        if not current.is_weekend():
            count += 1
        current = current.add_days(1)
    
    return count
