"""
Base Report Class
Abstract base class for all reports with common functionality
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Union
import logging

from utils import create_mavrick_db_manager, ExcelManager

logger = logging.getLogger(__name__)


class BaseReport(ABC):
    """
    Abstract base class for all reports.
    Provides common functionality and enforces consistent interface.
    """
    
    def __init__(self, report_name: str, output_dir: str = None, interim_dir: str = None):
        """
        Initialize base report.
        
        Args:
            report_name: Name of the report (used for folder structure)
            output_dir: Output directory (default: output_data/{report_name})
            interim_dir: Interim data directory (default: interim_data/{report_name})
        """
        self.report_name = report_name
        self.output_dir = Path(output_dir or f"output_data/{report_name}")
        self.interim_dir = Path(interim_dir or f"interim_data/{report_name}")
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.interim_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize managers
        self.db = None
        self.excel_mgr = ExcelManager(output_dir=str(self.output_dir))
        
        logger.info(f"{self.report_name} Report initialized")
    
    def connect_db(self):
        """Connect to MAVRICK database."""
        try:
            self.db = create_mavrick_db_manager()
            logger.info("Connected to MAVRICK database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    @abstractmethod
    def extract_data(self) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Extract data from database.
        Must be implemented by subclasses.
        
        Returns:
            Raw DataFrame from database, OR
            Dictionary of DataFrames keyed by data source name (for multiple queries)
            
        Examples:
            # Single query
            def extract_data(self) -> pd.DataFrame:
                return self.db.run_query_from_file("queries/single_query.sql")
            
            # Multiple queries
            def extract_data(self) -> Dict[str, pd.DataFrame]:
                return {
                    "models": self.db.run_query_from_file("queries/models.sql"),
                    "owners": self.db.run_query_from_file("queries/owners.sql"),
                    "metrics": self.db.run_query_from_file("queries/metrics.sql")
                }
        """
        pass
    
    @abstractmethod
    def transform_data(self, df_raw: Union[pd.DataFrame, Dict[str, pd.DataFrame]]) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Transform and clean data.
        Must be implemented by subclasses.
        
        Args:
            df_raw: Raw DataFrame from database, OR
                   Dictionary of DataFrames (if multiple queries were used)
            
        Returns:
            Cleaned and transformed DataFrame, OR
            Dictionary of cleaned DataFrames (maintaining same keys as input)
            
        Examples:
            # Single DataFrame
            def transform_data(self, df_raw: pd.DataFrame) -> pd.DataFrame:
                df = df_raw.copy()
                # ... transformation logic ...
                return df
            
            # Multiple DataFrames
            def transform_data(self, df_raw: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
                return {
                    "models": self._transform_models(df_raw["models"]),
                    "owners": self._transform_owners(df_raw["owners"]),
                    "metrics": self._transform_metrics(df_raw["metrics"])
                }
        """
        pass
    
    @abstractmethod
    def calculate_aggregations(self, df: pd.DataFrame) -> dict:
        """
        Calculate aggregations and prepare data for reporting.
        Must be implemented by subclasses.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Dictionary of DataFrames keyed by sheet name
        """
        pass
    
    def save_interim_data(self, df: pd.DataFrame, filename_prefix: str = None):
        """
        Save interim data for future use.
        
        Args:
            df: DataFrame to save
            filename_prefix: Prefix for filename (default: report_name)
        """
        logger.info("Saving interim data...")
        
        prefix = filename_prefix or self.report_name.lower().replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d")
        
        csv_path = self.interim_dir / f"{prefix}_data_{timestamp}.csv"
        
        df.to_csv(csv_path, index=False)
        
        logger.info(f"Interim data saved: {csv_path}")
    
    @abstractmethod
    def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
        """
        Generate report from aggregated data.
        Must be implemented by subclasses to handle report-specific formats.
        
        Args:
            aggregated_data: Dictionary of DataFrames keyed by sheet/table name
            filename_prefix: Prefix for filename (default: report_name)
            
        Returns:
            Path to generated report file
            
        Examples:
            # Excel report with multiple sheets
            def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
                file_path = self._get_output_path(filename_prefix, extension='.xlsx')
                return self.excel_mgr.save_multiple_dataframes(
                    dataframes=aggregated_data,
                    file_path=file_path,
                    index=False
                )
            
            # CSV report (single file)
            def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
                file_path = self._get_output_path(filename_prefix, extension='.csv')
                aggregated_data['Detail'].to_csv(file_path, index=False)
                return file_path
            
            # Multiple CSV files
            def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
                prefix = filename_prefix or self.report_name.replace(" ", "_")
                for sheet_name, df in aggregated_data.items():
                    file_path = self._get_output_path(f"{prefix}_{sheet_name}", extension='.csv')
                    df.to_csv(file_path, index=False)
                return self.output_dir  # Return directory if multiple files
        """
        pass
    
    def _get_output_path(self, filename_prefix: str = None, extension: str = '.xlsx', 
                         include_timestamp: bool = True) -> Path:
        """
        Helper method to generate output file path.
        
        Args:
            filename_prefix: Prefix for filename (default: report_name)
            extension: File extension (default: '.xlsx')
            include_timestamp: Whether to include timestamp in filename (default: True)
            
        Returns:
            Path object for output file
        """
        prefix = filename_prefix or self.report_name.replace(" ", "_")
        
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_Report_{timestamp}{extension}"
        else:
            filename = f"{prefix}_Report{extension}"
        
        return self.output_dir / filename
    
    def _generate_filename(self, prefix: str = None, suffix: str = "", 
                          extension: str = '.xlsx', include_timestamp: bool = True) -> str:
        """
        Helper method to generate filename string.
        
        Args:
            prefix: Filename prefix (default: report_name)
            suffix: Filename suffix (appended before extension)
            extension: File extension (default: '.xlsx')
            include_timestamp: Whether to include timestamp (default: True)
            
        Returns:
            Filename string
        """
        prefix = prefix or self.report_name.replace(" ", "_")
        
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if suffix:
                return f"{prefix}_{suffix}_{timestamp}{extension}"
            else:
                return f"{prefix}_{timestamp}{extension}"
        else:
            if suffix:
                return f"{prefix}_{suffix}{extension}"
            else:
                return f"{prefix}{extension}"
    
    def _is_multi_query(self, data: Union[pd.DataFrame, Dict]) -> bool:
        """Check if data is from multiple queries (dict) or single query (DataFrame)."""
        return isinstance(data, dict)
    
    def _save_interim_data_multi(self, data_dict: Dict[str, pd.DataFrame], filename_prefix: str = None):
        """Save multiple DataFrames as interim data."""
        prefix = filename_prefix or self.report_name.lower().replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d")
        
        for key, df in data_dict.items():
            csv_path = self.interim_dir / f"{prefix}_{key}_{timestamp}.csv"
            parquet_path = self.interim_dir / f"{prefix}_{key}_{timestamp}.parquet"
            
            df.to_csv(csv_path, index=False)
            df.to_parquet(parquet_path, index=False)
            
            logger.info(f"Interim data saved: {csv_path}, {parquet_path}")
    
    def run(self) -> Path:
        """
        Execute the complete report workflow.
        Supports both single and multiple queries.
        
        Returns:
            Path to generated Excel report
        """
        logger.info("=" * 60)
        logger.info(f"Starting {self.report_name} Report Generation")
        logger.info("=" * 60)
        
        try:
            # Step 1: Connect to database
            self.connect_db()
            
            # Step 2: Extract data (can be single DataFrame or dict of DataFrames)
            df_raw = self.extract_data()
            is_multi = self._is_multi_query(df_raw)
            
            if is_multi:
                logger.info(f"Extracted data from {len(df_raw)} queries")
            else:
                logger.info(f"Extracted {len(df_raw)} rows from database")
            
            # Step 3: Transform data
            df_clean = self.transform_data(df_raw)
            
            # Step 4: Save interim data
            if self._is_multi_query(df_clean):
                self._save_interim_data_multi(df_clean)
            else:
                self.save_interim_data(df_clean)
            
            # Step 5: Calculate aggregations
            # Note: calculate_aggregations should handle both single and multi-query cases
            aggregated_data = self.calculate_aggregations(df_clean)
            
            # Step 6: Generate report
            report_path = self.generate_report(aggregated_data)
            
            logger.info("=" * 60)
            logger.info(f"{self.report_name} Report Generation Completed Successfully")
            logger.info(f"Report saved to: {report_path}")
            logger.info("=" * 60)
            
            return report_path
        
        except Exception as e:
            logger.error(f"Report generation failed: {e}", exc_info=True)
            raise
        
        finally:
            # Close database connection
            if self.db:
                self.db.close()
