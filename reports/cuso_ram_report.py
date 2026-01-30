"""
CUSO RAM Report
Risk Appetite Measure Report
Processes model information from Model Governance team
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Union, Dict
import logging
from datetime import date

from .base_report import BaseReport
from utils import (
    MRGDate, 
    load_report_config_with_fallback,
    load_default_config,
    load_temp_config,
    apply_sheet_filters
)

logger = logging.getLogger(__name__)


class CUSORAMReport(BaseReport):
    """
    CUSO RAM (Risk Appetite Measure) Report Generator
    """

    @classmethod
    def from_config_file(
        cls,
        config_path: Union[str, Path],
        inventory_date: Optional[Union[str, MRGDate, date]] = None,
        compliance_date: Optional[Union[str, MRGDate, date]] = None,
    ) -> "CUSORAMReport":
        """
        Create a CUSO RAM Report instance from a configuration JSON file.

        Reads inventory_date, compliance_date, and sheet_filters from the file.
        Pass inventory_date or compliance_date to override the file values.

        Args:
            config_path: Path to the configuration JSON file
                        (e.g. "config/cuso_ram_report_config.json")
            inventory_date: Optional override for inventory date
            compliance_date: Optional override for compliance date

        Returns:
            Initialized CUSORAMReport instance

        Example:
            report = CUSORAMReport.from_config_file("config/cuso_ram_report_config.json")
            report.run()

            # Override one date from file
            report = CUSORAMReport.from_config_file(
                "config/cuso_ram_report_config.json",
                inventory_date="2026-06-30"
            )
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        return cls(
            inventory_date=inventory_date,
            compliance_date=compliance_date,
            config_file=str(path.resolve())
        )

    def __init__(self, 
                 inventory_date: Optional[Union[str, MRGDate, date]] = None,
                 compliance_date: Optional[Union[str, MRGDate, date]] = None,
                 config_file: Optional[str] = None):
        """
        Initialize CUSO RAM Report.
        
        Args:
            inventory_date: Inventory date (replaces (0=0) placeholder). Can be:
                           - MRGDate object
                           - String in format 'YYYY-MM-DD' (e.g., '2025-12-31')
                           - datetime.date object
                           - If None, tries to load from config file, then uses today's date
            compliance_date: Compliance date (replaces (10=10) placeholder). Can be:
                            - MRGDate object
                            - String in format 'YYYY-MM-DD' (e.g., '2025-12-31')
                            - datetime.date object
                            - If None, tries to load from config file, then uses same as inventory_date
            config_file: Configuration file specification. Can be:
                        - None: Use default loading logic (saved → default → generate)
                        - "default": Force use default configuration
                        - "temp:{timestamp}": Use temporary config with timestamp (e.g., "temp:20260129_143022")
                        - Path string: Use specific config file path
        """
        super().__init__(
            report_name="CUSO RAM Report",
            output_dir="output_data/cuso_ram",
            interim_dir="interim_data/cuso_ram"
        )
        
        # Load configuration based on config_file parameter
        # Use "CUSO RAM Report" to match the registered report name
        report_config_name = "CUSO RAM Report"
        self.config = None
        if config_file is None:
            # Use default loading logic: saved → default → generate
            self.config = load_report_config_with_fallback(report_config_name)
        elif config_file == "default":
            # Force use default configuration
            self.config = load_default_config(report_config_name)
            if self.config is None:
                from utils import get_default_report_config
                self.config = get_default_report_config(report_config_name)
        elif config_file.startswith("temp:"):
            # Load temporary config by timestamp
            timestamp = config_file.replace("temp:", "")
            self.config = load_temp_config(report_config_name, timestamp=timestamp)
            if self.config is None:
                logger.warning(f"Temp config with timestamp {timestamp} not found, using default")
                self.config = load_report_config_with_fallback(report_config_name)
        else:
            # Load from specific file path
            from pathlib import Path
            from utils.config_manager import get_config_manager
            config_manager = get_config_manager()
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    import json
                    with open(config_path, 'r', encoding='utf-8') as f:
                        self.config = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load config from {config_file}: {e}")
                    self.config = load_report_config_with_fallback(report_config_name)
            else:
                logger.warning(f"Config file {config_file} not found, using default")
                self.config = load_report_config_with_fallback(report_config_name)
        
        # Set inventory date: prioritize argument, then config, then default
        if inventory_date is None and self.config:
            inventory_date = self.config.get("inventory_date")
        
        if inventory_date is None:
            # Use today's date
            today = date.today()
            self.inventory_date_obj = MRGDate(today.day, today.month, today.year)
        elif isinstance(inventory_date, MRGDate):
            self.inventory_date_obj = inventory_date
        elif isinstance(inventory_date, date):
            self.inventory_date_obj = MRGDate.from_datetime(inventory_date)
        else:
            # String - try to parse using MRGDate
            self.inventory_date_obj = MRGDate.from_pandas(inventory_date)
        
        # Set compliance date: prioritize argument, then config, then default to inventory date
        if compliance_date is None and self.config:
            compliance_date = self.config.get("compliance_date")
        
        if compliance_date is None:
            self.compliance_date_obj = self.inventory_date_obj
        elif isinstance(compliance_date, MRGDate):
            self.compliance_date_obj = compliance_date
        elif isinstance(compliance_date, date):
            self.compliance_date_obj = MRGDate.from_datetime(compliance_date)
        else:
            # String - try to parse using MRGDate
            self.compliance_date_obj = MRGDate.from_pandas(compliance_date)
        
        # Store as strings in YYYY-MM-DD format for SQL queries
        self.inventory_date = self.inventory_date_obj.to_string('%Y-%m-%d')
        self.compliance_date = self.compliance_date_obj.to_string('%Y-%m-%d')
        
        logger.info(f"Inventory date set to: {self.inventory_date}")
        logger.info(f"Compliance date set to: {self.compliance_date}")
        
        # Store sheet filters from config
        self.sheet_filters = self.config.get("sheet_filters", {}) if self.config else {}

        # Report-specific config: Excel template and queries (per tab or single)
        self.excel_template_path = self.config.get("excel_template_path") if self.config else None
        self.query_path = self.config.get("query") if self.config else None
        self.tab_queries = self.config.get("tab_queries") or {}
        if self.tab_queries and not isinstance(self.tab_queries, dict):
            self.tab_queries = {}

    def _get_placeholders(self) -> dict:
        """Build placeholder dict for SQL query replacement."""
        return {
            "[DBName].[DBSchema]": "[DMAV_MAVRICK].[MAV2]",
            "(0=0)": f"M.DateStamp = '{self.inventory_date}'",
            "(10=10)": f"'{self.compliance_date}'",
        }

    def extract_data(self) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Extract model information from database.
        Uses config: tab_queries (sheet -> query path) or query (single path).
        If neither is set, falls back to default query path.

        Returns:
            Single DataFrame, or dict of sheet_name -> DataFrame when tab_queries is configured
        """
        logger.info("Extracting model data from database...")
        if not self.db:
            self.connect_db()
        placeholders = self._get_placeholders()

        # Multiple queries per tab (from config tab_queries)
        if self.tab_queries:
            result = {}
            for sheet_name, query_path in self.tab_queries.items():
                path = Path(query_path)
                if not path.exists():
                    logger.warning(f"Query file not found for sheet '{sheet_name}': {path}")
                    result[sheet_name] = pd.DataFrame()
                    continue
                try:
                    df = self.db.run_query_from_file(path, placeholders=placeholders)
                    result[sheet_name] = df
                    logger.info(f"Extracted {len(df)} rows for sheet '{sheet_name}' from {path}")
                except Exception as e:
                    logger.error(f"Failed to run query for sheet '{sheet_name}': {e}")
                    result[sheet_name] = pd.DataFrame()
            return result

        # Single query (from config query or fallback)
        query_path = self.query_path or "queries/Risk Appetite Measure (RAM) Models_New.sql"
        query_file = Path(query_path)
        if not query_file.exists():
            raise FileNotFoundError(f"Query file not found: {query_file}")
        try:
            df_raw = self.db.run_query_from_file(query_file, placeholders=placeholders)
            logger.info(f"Extracted {len(df_raw)} rows from database")
            return df_raw
        except Exception as e:
            logger.error(f"Failed to extract data: {e}")
            raise
    
    def _transform_single(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Transform a single DataFrame (cleaning, types, etc.)."""
        df = df_raw.copy()
        # TODO: Add data cleaning and transformation logic
        return df

    def transform_data(
        self, df_raw: Union[pd.DataFrame, Dict[str, pd.DataFrame]]
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Clean and transform raw data.
        Handles both single DataFrame and dict of DataFrames (when tab_queries is used).
        """
        logger.info("Transforming data...")
        if isinstance(df_raw, dict):
            result = {k: self._transform_single(v) for k, v in df_raw.items()}
            logger.info(f"Transformed {len(result)} sheets")
            return result
        df = self._transform_single(df_raw)
        logger.info(f"Transformed data: {len(df)} rows")
        return df

    def calculate_aggregations(
        self, df: Union[pd.DataFrame, Dict[str, pd.DataFrame]]
    ) -> dict:
        """
        Calculate aggregations by model owner and other dimensions.
        Handles both single DataFrame and dict of DataFrames (when tab_queries is used).
        TODO: Implement specific aggregation logic after reviewing query results.
        """
        logger.info("Calculating aggregations...")
        if isinstance(df, dict):
            # Multi-tab: passthrough or add aggregation logic per sheet
            aggregated_data = {k: v for k, v in df.items() if not v.empty}
            logger.info(f"Returning {len(aggregated_data)} sheets (aggregation logic to be implemented)")
            return aggregated_data
        # Single query: one sheet
        aggregated_data = {"Detail": df}
        logger.info(f"Returning {len(df)} rows (aggregation logic to be implemented)")
        return aggregated_data
    
    def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
        """
        Generate Excel report from aggregated data.
        Applies filters from configuration if available.
        
        Args:
            aggregated_data: Dictionary of DataFrames keyed by sheet name
            filename_prefix: Prefix for filename (default: report_name)
            
        Returns:
            Path to generated Excel file
        """
        logger.info("Generating Excel report...")
        
        # Apply filters if configured
        if self.sheet_filters:
            logger.info("Applying sheet filters from configuration...")
            aggregated_data = apply_sheet_filters(aggregated_data, self.sheet_filters)

        file_path = self._get_output_path(filename_prefix, extension=".xlsx")

        if not aggregated_data:
            pd.DataFrame().to_excel(file_path, index=False)
            logger.info(f"Report generated (empty): {file_path}")
            return file_path

        template_path = None
        if self.excel_template_path:
            p = Path(self.excel_template_path)
            if p.exists():
                template_path = p
            else:
                logger.warning(f"Excel template not found: {p}, saving without template")

        if template_path:
            self.excel_mgr.save_dataframes_to_template(
                template_path=template_path,
                dataframes=aggregated_data,
                output_path=file_path,
                index=False,
            )
        else:
            self.excel_mgr.save_multiple_dataframes(
                dataframes=aggregated_data,
                file_path=file_path,
                index=False,
            )
        logger.info(f"Report generated: {file_path}")
        return file_path


def main():
    """Main function to run the report."""
    report = CUSORAMReport()
    report.run()


if __name__ == "__main__":
    main()
