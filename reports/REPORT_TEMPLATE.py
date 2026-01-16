"""
Report Template
Use this as a template for creating new reports

Copy this file and rename it to your_report_name_report.py
Then implement the abstract methods from BaseReport

Note: Database and Excel managers are available through BaseReport
"""

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
    
    def extract_data(self) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Extract data from database.
        
        Returns:
            Raw DataFrame from database (single query), OR
            Dictionary of DataFrames (multiple queries)
        """
        logger.info("Extracting data from database...")
        
        # Option 1: Single query from file
        query_file = Path("queries/your_query_name.sql")
        df_raw = self.db.run_query_from_file(query_file)
        logger.info(f"Extracted {len(df_raw)} rows from database")
        return df_raw
        
        # Option 2: Multiple queries
        # return {
        #     "main_data": self.db.run_query_from_file(Path("queries/main_query.sql")),
        #     "reference_data": self.db.run_query_from_file(Path("queries/reference.sql")),
        #     "lookup_data": self.db.run_query_from_string("SELECT * FROM lookup_table")
        # }
        
        # Option 3: Use inline query with parameters
        # query = "SELECT * FROM your_table WHERE condition = :param"
        # df_raw = self.db.run_query_from_string(query, params={"param": "value"})
        # return df_raw
    
    def transform_data(self, df_raw: Union[pd.DataFrame, Dict[str, pd.DataFrame]]) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Transform and clean data.
        
        Args:
            df_raw: Raw DataFrame from database (single query), OR
                   Dictionary of DataFrames (multiple queries)
            
        Returns:
            Cleaned and transformed DataFrame, OR
            Dictionary of cleaned DataFrames (maintaining same keys)
        """
        logger.info("Transforming data...")
        
        # Handle single DataFrame
        if isinstance(df_raw, pd.DataFrame):
            df = df_raw.copy()
            # Add your data transformation logic here:
            # - Remove duplicates
            # - Handle missing values
            # - Standardize column names
            # - Convert data types
            # - Add calculated columns
            logger.info(f"Transformed data: {len(df)} rows")
            return df
        
        # Handle multiple DataFrames
        else:
            transformed = {}
            for key, df in df_raw.items():
                df_clean = df.copy()
                # Add transformation logic for each DataFrame
                # transformed[key] = self._transform_specific(df_clean)
                transformed[key] = df_clean
                logger.info(f"Transformed {key}: {len(df_clean)} rows")
            return transformed
    
    def calculate_aggregations(self, df: Union[pd.DataFrame, Dict[str, pd.DataFrame]]) -> dict:
        """
        Calculate aggregations and prepare data for reporting.
        
        Args:
            df: Cleaned DataFrame (single query), OR
                Dictionary of cleaned DataFrames (multiple queries)
            
        Returns:
            Dictionary of DataFrames keyed by sheet name
        """
        logger.info("Calculating aggregations...")
        
        aggregated_data = {}
        
        # Handle single DataFrame
        if isinstance(df, pd.DataFrame):
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
        
        # Handle multiple DataFrames
        else:
            # You can merge/join DataFrames here, or keep them separate
            # Example: Merge main_data with reference_data
            # merged = df['main_data'].merge(df['reference_data'], on='key', how='left')
            
            # Add each DataFrame as a sheet
            for key, df_item in df.items():
                aggregated_data[key] = df_item
            
            # Or create combined aggregations
            # aggregated_data['Combined_Summary'] = self._create_combined_summary(df)
        
        logger.info(f"Created {len(aggregated_data)} aggregated datasets")
        return aggregated_data
    
    def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
        """
        Generate report from aggregated data.
        Customize this method based on your report's output format requirements.
        
        Args:
            aggregated_data: Dictionary of DataFrames keyed by sheet/table name
            filename_prefix: Prefix for filename (default: report_name)
            
        Returns:
            Path to generated report file
            
        Examples:
            # Option 1: Standard Excel with multiple sheets (most common)
            def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
                file_path = self._get_output_path(filename_prefix, extension='.xlsx')
                return self.excel_mgr.save_multiple_dataframes(
                    dataframes=aggregated_data,
                    file_path=file_path,
                    index=False,
                    format_header=True,
                    auto_adjust_width=True
                )
            
            # Option 2: Single CSV file
            def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
                file_path = self._get_output_path(filename_prefix, extension='.csv')
                aggregated_data['Detail'].to_csv(file_path, index=False)
                return file_path
            
            # Option 3: Multiple CSV files (one per sheet)
            def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
                prefix = filename_prefix or self.report_name.replace(" ", "_")
                for sheet_name, df in aggregated_data.items():
                    file_path = self._get_output_path(f"{prefix}_{sheet_name}", extension='.csv')
                    df.to_csv(file_path, index=False)
                return self.output_dir  # Return directory if multiple files
            
            # Option 4: Custom Excel format with specific cell locations
            def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
                file_path = self._get_output_path(filename_prefix, extension='.xlsx')
                # Create workbook
                from openpyxl import Workbook
                wb = Workbook()
                ws = wb.active
                ws.title = "Summary"
                # Add custom formatting, charts, etc.
                wb.save(file_path)
                return file_path
        """
        # Default implementation: Excel with multiple sheets
        logger.info("Generating Excel report...")
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


# To register this report, add to reports/__init__.py:
# from .your_report_name_report import YourReportNameReport
# register_report("your_report_name", YourReportNameReport)
