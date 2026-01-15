"""
Base Report Class
Abstract base class for all reports with common functionality
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
import logging

from db_manager import create_mavrick_db_manager
from excel_manager import ExcelManager

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
    def extract_data(self) -> pd.DataFrame:
        """
        Extract data from database.
        Must be implemented by subclasses.
        
        Returns:
            Raw DataFrame from database
        """
        pass
    
    @abstractmethod
    def transform_data(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Transform and clean data.
        Must be implemented by subclasses.
        
        Args:
            df_raw: Raw DataFrame from database
            
        Returns:
            Cleaned and transformed DataFrame
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
        parquet_path = self.interim_dir / f"{prefix}_data_{timestamp}.parquet"
        
        df.to_csv(csv_path, index=False)
        df.to_parquet(parquet_path, index=False)
        
        logger.info(f"Interim data saved: {csv_path}, {parquet_path}")
    
    def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
        """
        Generate Excel report from aggregated data.
        
        Args:
            aggregated_data: Dictionary of DataFrames keyed by sheet name
            filename_prefix: Prefix for filename (default: report_name)
            
        Returns:
            Path to generated Excel file
        """
        logger.info("Generating Excel report...")
        
        prefix = filename_prefix or self.report_name.replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_Report_{timestamp}.xlsx"
        file_path = self.output_dir / filename
        
        # Save all DataFrames to Excel with multiple sheets
        excel_path = self.excel_mgr.save_multiple_dataframes(
            dataframes=aggregated_data,
            file_path=file_path,
            index=False,
            format_header=True,
            auto_adjust_width=True
        )
        
        logger.info(f"Report generated: {excel_path}")
        return excel_path
    
    def run(self) -> Path:
        """
        Execute the complete report workflow.
        
        Returns:
            Path to generated Excel report
        """
        logger.info("=" * 60)
        logger.info(f"Starting {self.report_name} Report Generation")
        logger.info("=" * 60)
        
        try:
            # Step 1: Connect to database
            self.connect_db()
            
            # Step 2: Extract data
            df_raw = self.extract_data()
            
            # Step 3: Transform data
            df_clean = self.transform_data(df_raw)
            
            # Step 4: Save interim data
            self.save_interim_data(df_clean)
            
            # Step 5: Calculate aggregations
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
