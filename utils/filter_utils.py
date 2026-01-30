"""
Filter Utilities
Functions to apply filters to DataFrames based on configuration
"""

import pandas as pd
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def _parse_comma_separated_values(value: Any) -> list:
    """Parse value into a list of strings. Accepts comma-separated string or list."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    s = str(value).strip()
    if not s:
        return []
    return [v.strip() for v in s.split(",") if v.strip()]


def apply_filter_to_dataframe(df: pd.DataFrame, column_name: str, 
                             filter_config: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply a single filter to a DataFrame column.
    
    Args:
        df: DataFrame to filter
        column_name: Name of the column to filter
        filter_config: Filter configuration dictionary with keys:
            - operator: Filter operator (equals, contains, etc.)
            - value: Filter value(s)
            - enabled: Whether filter is enabled
    
    Returns:
        Filtered DataFrame
    """
    if not filter_config.get("enabled", False):
        return df
    
    if column_name not in df.columns:
        logger.warning(f"Column '{column_name}' not found in DataFrame. Available columns: {list(df.columns)}")
        return df
    
    operator = filter_config.get("operator", "equals")
    value = filter_config.get("value")
    
    try:
        if operator == "equals":
            return df[df[column_name] == value]
        
        elif operator == "not_equals":
            return df[df[column_name] != value]
        
        elif operator == "contains":
            # Support multiple values separated by comma: match if column contains ANY of them
            values = _parse_comma_separated_values(value)
            if not values:
                return df
            col_str = df[column_name].astype(str)
            mask = col_str.str.contains(values[0], case=False, na=False)
            for v in values[1:]:
                mask = mask | col_str.str.contains(str(v).strip(), case=False, na=False)
            return df[mask]

        elif operator == "not_contains":
            # Support multiple values separated by comma: match if column contains NONE of them
            values = _parse_comma_separated_values(value)
            if not values:
                return df
            col_str = df[column_name].astype(str)
            mask = ~col_str.str.contains(values[0], case=False, na=False)
            for v in values[1:]:
                mask = mask & ~col_str.str.contains(str(v).strip(), case=False, na=False)
            return df[mask]
        
        elif operator == "starts_with":
            return df[df[column_name].astype(str).str.startswith(str(value), na=False)]
        
        elif operator == "ends_with":
            return df[df[column_name].astype(str).str.endswith(str(value), na=False)]
        
        elif operator == "greater_than":
            return df[df[column_name] > value]
        
        elif operator == "less_than":
            return df[df[column_name] < value]
        
        elif operator == "greater_equal":
            return df[df[column_name] >= value]
        
        elif operator == "less_equal":
            return df[df[column_name] <= value]
        
        elif operator == "in_list":
            if isinstance(value, list):
                return df[df[column_name].isin(value)]
            else:
                return df[df[column_name] == value]
        
        elif operator == "not_in_list":
            if isinstance(value, list):
                return df[~df[column_name].isin(value)]
            else:
                return df[df[column_name] != value]
        
        elif operator == "is_null":
            return df[df[column_name].isna()]
        
        elif operator == "is_not_null":
            return df[df[column_name].notna()]
        
        elif operator == "between":
            if isinstance(value, list) and len(value) >= 2:
                min_val, max_val = value[0], value[1]
                if min_val and max_val:
                    return df[(df[column_name] >= min_val) & (df[column_name] <= max_val)]
                elif min_val:
                    return df[df[column_name] >= min_val]
                elif max_val:
                    return df[df[column_name] <= max_val]
            return df
        
        else:
            logger.warning(f"Unknown filter operator: {operator}")
            return df
    
    except Exception as e:
        logger.error(f"Error applying filter {operator} to column {column_name}: {e}")
        return df


def apply_sheet_filters(aggregated_data: Dict[str, pd.DataFrame], 
                        sheet_filters: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, pd.DataFrame]:
    """
    Apply filters to all sheets in aggregated data based on configuration.
    
    Args:
        aggregated_data: Dictionary of DataFrames keyed by sheet name
        sheet_filters: Dictionary of filters keyed by sheet name, then column name
        
    Returns:
        Dictionary of filtered DataFrames
    """
    filtered_data = {}
    
    for sheet_name, df in aggregated_data.items():
        filtered_df = df.copy()
        
        # Apply filters for this sheet if configured
        if sheet_name in sheet_filters:
            column_filters = sheet_filters[sheet_name]
            
            for column_name, filter_config in column_filters.items():
                if filter_config.get("enabled", False):
                    rows_before = len(filtered_df)
                    filtered_df = apply_filter_to_dataframe(filtered_df, column_name, filter_config)
                    rows_after = len(filtered_df)
                    
                    logger.info(
                        f"Applied filter to sheet '{sheet_name}', column '{column_name}': "
                        f"{rows_before} -> {rows_after} rows"
                    )
        
        filtered_data[sheet_name] = filtered_df
    
    return filtered_data
