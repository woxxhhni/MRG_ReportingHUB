"""
Report Template
Use this as a template for creating new reports

Copy this file and rename it to your_report_name_report.py
Then implement the abstract methods from BaseReport
"""

import pandas as pd
from pathlib import Path
import logging

from .base_report import BaseReport

logger = logging.getLogger(__name__)


class YourReportNameReport(BaseReport):
    """
    Your Report Name Report Generator
    
    Description: Brief description of what this report does
    """
    
    def __init__(self):
        """Initialize Your Report Name Report."""
        super().__init__(
            report_name="Your Report Name",
            output_dir="output_data/your_report_name",
            interim_dir="interim_data/your_report_name"
        )
    
    def extract_data(self) -> pd.DataFrame:
        """
        Extract data from database.
        
        Returns:
            Raw DataFrame from database
        """
        logger.info("Extracting data from database...")
        
        # Option 1: Load query from file
        query_file = Path("queries/your_query_name.sql")
        df_raw = self.db.run_query_from_file(query_file)
        
        # Option 2: Use inline query
        # query = "SELECT * FROM your_table WHERE condition = :param"
        # df_raw = self.db.run_query_from_string(query, params={"param": "value"})
        
        logger.info(f"Extracted {len(df_raw)} rows from database")
        return df_raw
    
    def transform_data(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Transform and clean data.
        
        Args:
            df_raw: Raw DataFrame from database
            
        Returns:
            Cleaned and transformed DataFrame
        """
        logger.info("Transforming data...")
        
        df = df_raw.copy()
        
        # Add your data transformation logic here:
        # - Remove duplicates
        # - Handle missing values
        # - Standardize column names
        # - Convert data types
        # - Add calculated columns
        # etc.
        
        logger.info(f"Transformed data: {len(df)} rows")
        return df
    
    def calculate_aggregations(self, df: pd.DataFrame) -> dict:
        """
        Calculate aggregations and prepare data for reporting.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Dictionary of DataFrames keyed by sheet name
        """
        logger.info("Calculating aggregations...")
        
        aggregated_data = {}
        
        # Example: Summary by category
        if 'category' in df.columns:
            df_by_category = df.groupby('category').agg({
                # Add your aggregation logic here
                # 'value': ['sum', 'mean', 'count'],
            }).reset_index()
            aggregated_data['Summary_by_Category'] = df_by_category
        
        # Example: Overall summary
        summary_stats = pd.DataFrame({
            'Metric': ['Total Records', 'Date Range'],
            'Value': [
                len(df),
                f"{df['date'].min()} to {df['date'].max()}" if 'date' in df.columns else 'N/A'
            ]
        })
        aggregated_data['Overall_Summary'] = summary_stats
        
        # Always include detail data
        aggregated_data['Detail'] = df
        
        logger.info(f"Created {len(aggregated_data)} aggregated datasets")
        return aggregated_data


# To register this report, add to reports/__init__.py:
# from .your_report_name_report import YourReportNameReport
# register_report("your_report_name", YourReportNameReport)
