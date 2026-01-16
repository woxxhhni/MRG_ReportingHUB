"""
Example: Report with Multiple Queries
This demonstrates how to create a report that uses multiple SQL queries
"""

import pandas as pd
from pathlib import Path
from typing import Union, Dict
import logging

from .base_report import BaseReport

logger = logging.getLogger(__name__)


class MultiQueryReportExample(BaseReport):
    """
    Example report that uses multiple queries.
    
    This report demonstrates:
    1. Extracting data from multiple queries
    2. Transforming multiple DataFrames
    3. Merging/joining DataFrames
    4. Creating aggregations from combined data
    """
    
    def __init__(self):
        """Initialize Multi-Query Report."""
        super().__init__(
            report_name="Multi Query Example",
            output_dir="output_data/multi_query_example",
            interim_dir="interim_data/multi_query_example"
        )
    
    def extract_data(self) -> Dict[str, pd.DataFrame]:
        """
        Extract data from multiple queries.
        
        Returns:
            Dictionary of DataFrames keyed by data source name
        """
        logger.info("Extracting data from multiple queries...")
        
        if not self.db:
            self.connect_db()
        
        # Execute multiple queries
        data = {
            "main_data": self.db.run_query_from_file(
                Path("queries/main_query.sql")
            ),
            "reference_data": self.db.run_query_from_file(
                Path("queries/reference_data.sql")
            ),
            "lookup_table": self.db.run_query_from_string(
                "SELECT * FROM lookup_table WHERE active = 1"
            )
        }
        
        logger.info(f"Extracted data from {len(data)} queries:")
        for key, df in data.items():
            logger.info(f"  - {key}: {len(df)} rows")
        
        return data
    
    def transform_data(self, df_raw: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Transform multiple DataFrames.
        
        Args:
            df_raw: Dictionary of raw DataFrames
            
        Returns:
            Dictionary of cleaned DataFrames
        """
        logger.info("Transforming multiple DataFrames...")
        
        transformed = {}
        
        # Transform main data
        df_main = df_raw["main_data"].copy()
        # Add transformation logic for main data
        # df_main = df_main.drop_duplicates()
        # df_main['date'] = pd.to_datetime(df_main['date'])
        transformed["main_data"] = df_main
        
        # Transform reference data
        df_ref = df_raw["reference_data"].copy()
        # Add transformation logic for reference data
        transformed["reference_data"] = df_ref
        
        # Transform lookup table
        df_lookup = df_raw["lookup_table"].copy()
        transformed["lookup_table"] = df_lookup
        
        logger.info("Transformation completed for all DataFrames")
        return transformed
    
    def calculate_aggregations(self, df: Dict[str, pd.DataFrame]) -> dict:
        """
        Calculate aggregations from multiple DataFrames.
        Can merge/join DataFrames here if needed.
        
        Args:
            df: Dictionary of cleaned DataFrames
            
        Returns:
            Dictionary of DataFrames for Excel sheets
        """
        logger.info("Calculating aggregations from multiple DataFrames...")
        
        aggregated_data = {}
        
        # Option 1: Keep DataFrames separate as different sheets
        aggregated_data["Main_Data"] = df["main_data"]
        aggregated_data["Reference_Data"] = df["reference_data"]
        aggregated_data["Lookup_Table"] = df["lookup_table"]
        
        # Option 2: Merge/Join DataFrames
        # Example: Merge main_data with reference_data
        # merged = df["main_data"].merge(
        #     df["reference_data"],
        #     on="common_key",
        #     how="left"
        # )
        # aggregated_data["Merged_Data"] = merged
        
        # Option 3: Create aggregations from merged data
        # if "common_key" in df["main_data"].columns:
        #     summary = df["main_data"].groupby("common_key").agg({
        #         "value": ["sum", "mean", "count"]
        #     }).reset_index()
        #     aggregated_data["Summary"] = summary
        
        # Option 4: Create cross-reference analysis
        # cross_ref = pd.crosstab(
        #     df["main_data"]["category"],
        #     df["main_data"]["status"]
        # )
        # aggregated_data["Cross_Reference"] = cross_ref
        
        logger.info(f"Created {len(aggregated_data)} aggregated datasets")
        return aggregated_data
    
    def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
        """
        Generate Excel report from aggregated data.
        Multiple DataFrames will be saved as separate sheets.
        
        Args:
            aggregated_data: Dictionary of DataFrames keyed by sheet name
            filename_prefix: Prefix for filename (default: report_name)
            
        Returns:
            Path to generated Excel file
        """
        logger.info("Generating Excel report with multiple sheets...")
        file_path = self._get_output_path(filename_prefix, extension='.xlsx')
        
        excel_path = self.excel_mgr.save_multiple_dataframes(
            dataframes=aggregated_data,
            file_path=file_path,
            index=False,
            format_header=True,
            auto_adjust_width=True
        )
        
        logger.info(f"Report generated: {excel_path}")
        return excel_path
