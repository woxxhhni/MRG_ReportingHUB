"""
CUSO RAM Report
Risk Appetite Measure Report
Processes model information from Model Governance team
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Union
import logging
from datetime import date

from .base_report import BaseReport
from utils import MRGDate

logger = logging.getLogger(__name__)


class CUSORAMReport(BaseReport):
    """
    CUSO RAM (Risk Appetite Measure) Report Generator
    """
    
    def __init__(self, data_stamp_date: Optional[Union[str, MRGDate, date]] = None):
        """
        Initialize CUSO RAM Report.
        
        Args:
            data_stamp_date: Data stamp date. Can be:
                           - MRGDate object
                           - String in format 'YYYY-MM-DD' (e.g., '2025-12-31')
                           - datetime.date object
                           - If None, uses today's date
        """
        super().__init__(
            report_name="CUSO RAM",
            output_dir="output_data/cuso_ram",
            interim_dir="interim_data/cuso_ram"
        )
        
        # Set data stamp date using MRGDate class
        if data_stamp_date is None:
            # Use today's date
            today = date.today()
            self.data_stamp_date_obj = MRGDate(today.day, today.month, today.year)
        elif isinstance(data_stamp_date, MRGDate):
            self.data_stamp_date_obj = data_stamp_date
        elif isinstance(data_stamp_date, date):
            self.data_stamp_date_obj = MRGDate.from_datetime(data_stamp_date)
        else:
            # String - try to parse using MRGDate
            self.data_stamp_date_obj = MRGDate.from_pandas(data_stamp_date)
        
        # Store as string in YYYY-MM-DD format for SQL query
        self.data_stamp_date = self.data_stamp_date_obj.to_string('%Y-%m-%d')
        
        logger.info(f"Data stamp date set to: {self.data_stamp_date}")
    
    def extract_data(self) -> pd.DataFrame:
        """
        Extract model information from database.
        
        Returns:
            DataFrame with raw model data
        """
        logger.info("Extracting model data from database...")
        
        query_file = Path("queries/Risk Appetite Measure (RAM) Models_New.sql")
        
        if not query_file.exists():
            raise FileNotFoundError(f"Query file not found: {query_file}")
        
        if not self.db:
            self.connect_db()
        
        try:
            # Define placeholders for query replacement
            placeholders = {
                "[DBName].[DBSchema]": "[DMAV_MAVRICK].[MAV2]",
                "(0=0)": f"M.DataStamp = '{self.data_stamp_date}'"
            }
            
            df_raw = self.db.run_query_from_file(query_file, placeholders=placeholders)
            logger.info(f"Extracted {len(df_raw)} rows from database")
            return df_raw
        except Exception as e:
            logger.error(f"Failed to extract data: {e}")
            raise
    
    def transform_data(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and transform raw data.
        
        Args:
            df_raw: Raw DataFrame from database
            
        Returns:
            Cleaned and transformed DataFrame
        """
        logger.info("Transforming data...")
        
        df = df_raw.copy()
        
        # TODO: Add data cleaning and transformation logic
        # Examples:
        # - Remove duplicates
        # - Handle missing values
        # - Standardize column names
        # - Convert data types
        
        logger.info(f"Transformed data: {len(df)} rows")
        return df
    
    def calculate_aggregations(self, df: pd.DataFrame) -> dict:
        """
        Calculate aggregations by model owner and other dimensions.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Dictionary of aggregated DataFrames
        """
        logger.info("Calculating aggregations...")
        
        aggregated_data = {}
        
        # TODO: Update column names based on actual data structure
        # Example aggregations:
        
        # 1. Summary by Model Owner
        if 'model_owner' in df.columns:
            df_by_owner = df.groupby('model_owner').agg({
                # Add aggregation columns based on your requirements
                # Example:
                # 'model_id': 'count',
                # 'risk_score': ['mean', 'max', 'min'],
                # 'status': lambda x: x.value_counts().to_dict()
            }).reset_index()
            aggregated_data['Summary_by_Owner'] = df_by_owner
            logger.info(f"Created summary by model owner: {len(df_by_owner)} rows")
        
        # 2. Summary by Model Type (if exists)
        if 'model_type' in df.columns:
            df_by_type = df.groupby('model_type').agg({
                # Add aggregation logic
            }).reset_index()
            aggregated_data['Summary_by_Type'] = df_by_type
            logger.info(f"Created summary by model type: {len(df_by_type)} rows")
        
        # 3. Overall Summary
        summary_stats = pd.DataFrame({
            'Metric': ['Total Models', 'Unique Owners', 'Date Range'],
            'Value': [
                len(df),
                df['model_owner'].nunique() if 'model_owner' in df.columns else 0,
                f"{df['date'].min()} to {df['date'].max()}" if 'date' in df.columns else 'N/A'
            ]
        })
        aggregated_data['Overall_Summary'] = summary_stats
        
        # 4. Detail data (original cleaned data)
        aggregated_data['Detail'] = df
        
        logger.info(f"Created {len(aggregated_data)} aggregated datasets")
        return aggregated_data
    


def main():
    """Main function to run the report."""
    report = CUSORAMReport()
    report.run()


if __name__ == "__main__":
    main()
