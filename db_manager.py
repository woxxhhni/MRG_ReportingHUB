"""
Database Manager for MAVRICK DB
Handles SQL Server connections and basic database operations
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from pathlib import Path
from typing import Optional, Dict, List, Union
import logging
import os

logger = logging.getLogger(__name__)


class DBManager:
    """
    Database manager for MAVRICK DB (SQL Server).
    Provides methods for query execution and data operations.
    """
    
    def __init__(self, server: str, database: str, username: Optional[str] = None,
                 password: Optional[str] = None, driver: str = "ODBC Driver 17 for SQL Server",
                 use_windows_auth: bool = True, pool_size: int = 5):
        """
        Initialize database connection.
        
        Args:
            server: SQL Server name/address
            database: Database name
            username: Username (if using SQL authentication)
            password: Password (if using SQL authentication)
            driver: ODBC driver name
            use_windows_auth: Use Windows authentication (default: True)
            pool_size: Connection pool size
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.use_windows_auth = use_windows_auth
        self.pool_size = pool_size
        
        self.engine = None
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        try:
            if self.use_windows_auth:
                # Windows Authentication
                connection_string = (
                    f"mssql+pyodbc://{self.server}/{self.database}?"
                    f"driver={self.driver.replace(' ', '+')}&"
                    f"trusted_connection=yes"
                )
            else:
                # SQL Authentication
                connection_string = (
                    f"mssql+pyodbc://{self.username}:{self.password}@"
                    f"{self.server}/{self.database}?"
                    f"driver={self.driver.replace(' ', '+')}"
                )
            
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=10,
                pool_pre_ping=True,  # Verify connections before using
                echo=False
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info(f"Successfully connected to {self.server}/{self.database}")
        
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def run_query_from_string(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Execute a SQL query from a string and return results as DataFrame.
        
        Args:
            query: SQL query string
            params: Optional parameters for parameterized queries (dict)
            
        Returns:
            pandas DataFrame with query results
        """
        try:
            if params:
                # Use parameterized query
                df = pd.read_sql(text(query), self.engine, params=params)
            else:
                df = pd.read_sql(text(query), self.engine)
            
            logger.info(f"Query executed successfully. Rows returned: {len(df)}")
            return df
        
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query[:200]}...")  # Log first 200 chars
            raise
    
    def run_query_from_file(self, file_path: Union[str, Path], params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Execute a SQL query from a file and return results as DataFrame.
        
        Args:
            file_path: Path to SQL file (str or Path)
            params: Optional parameters for parameterized queries (dict)
            
        Returns:
            pandas DataFrame with query results
        """
        sql_file = Path(file_path)
        
        if not sql_file.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_file}")
        
        if not sql_file.is_file():
            raise ValueError(f"Path is not a file: {sql_file}")
        
        try:
            query = sql_file.read_text(encoding='utf-8')
            
            logger.info(f"Reading query from file: {sql_file}")
            return self.run_query_from_string(query, params)
        
        except Exception as e:
            logger.error(f"Failed to execute query from file {sql_file}: {e}")
            raise
    
    def insert_dataframe(self, df: pd.DataFrame, table_name: str, 
                        schema: Optional[str] = None, if_exists: str = "append",
                        chunksize: int = 1000, index: bool = False) -> int:
        """
        Insert rows from a DataFrame into a database table.
        
        Args:
            df: pandas DataFrame to insert
            table_name: Target table name
            schema: Optional schema name (default: dbo)
            if_exists: What to do if table exists - 'fail', 'replace', or 'append' (default)
            chunksize: Number of rows to insert per chunk
            index: Whether to write DataFrame index as a column
            
        Returns:
            Number of rows inserted
        """
        if df.empty:
            logger.warning("DataFrame is empty, nothing to insert")
            return 0
        
        try:
            full_table_name = f"{schema}.{table_name}" if schema else table_name
            
            rows_inserted = df.to_sql(
                name=table_name,
                con=self.engine,
                schema=schema,
                if_exists=if_exists,
                index=index,
                chunksize=chunksize,
                method='multi'  # Use multi-row insert for better performance
            )
            
            logger.info(f"Successfully inserted {len(df)} rows into {full_table_name}")
            return len(df)
        
        except Exception as e:
            logger.error(f"Failed to insert data into {table_name}: {e}")
            raise
    
    def execute_non_query(self, sql: str, params: Optional[Dict] = None) -> int:
        """
        Execute a non-query SQL statement (INSERT, UPDATE, DELETE, etc.).
        
        Args:
            sql: SQL statement string
            params: Optional parameters for parameterized queries
            
        Returns:
            Number of rows affected
        """
        try:
            with self.engine.begin() as conn:
                if params:
                    result = conn.execute(text(sql), params)
                else:
                    result = conn.execute(text(sql))
                rows_affected = result.rowcount
                conn.commit()
            
            logger.info(f"Non-query executed. Rows affected: {rows_affected}")
            return rows_affected
        
        except Exception as e:
            logger.error(f"Failed to execute non-query: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Connection test successful")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def close(self):
        """Close database connection and dispose of engine."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Factory function for MAVRICK DB
def create_mavrick_db_manager(server: Optional[str] = None,
                              database: Optional[str] = None,
                              use_windows_auth: bool = True) -> DBManager:
    """
    Factory function to create MAVRICK DB manager.
    Can use environment variables if parameters not provided.
    
    Default connection:
    - Server: YKE0-P19SP1301.fg.rbc.com\IN01
    - Database: DMAV_MAVRICK
    - Authentication: Windows (trusted_connection=yes)
    
    Args:
        server: SQL Server name (or use MAVRICK_DB_SERVER env var)
        database: Database name (or use MAVRICK_DB_NAME env var)
        use_windows_auth: Use Windows authentication
        
    Returns:
        DBManager instance
    """
    server = server or os.getenv(
        "MAVRICK_DB_SERVER", 
        r"YKE0-P19SP1301.fg.rbc.com\IN01"
    )
    database = database or os.getenv("MAVRICK_DB_NAME", "DMAV_MAVRICK")
    
    return DBManager(
        server=server,
        database=database,
        use_windows_auth=use_windows_auth
    )
