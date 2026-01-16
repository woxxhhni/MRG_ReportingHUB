"""
Configuration example for MAVRICK DB connection
You can copy this file to config.py and update with your actual credentials
"""

# MAVRICK DB Connection Configuration
MAVRICK_DB_CONFIG = {
    "server": r"YKE0-P19SP1301.fg.rbc.com\IN01",
    "database": "DMAV_MAVRICK",
    "driver": "ODBC Driver 17 for SQL Server",
    "use_windows_auth": True,  # Use Windows authentication
    "pool_size": 5
}

# Alternative: SQL Authentication (if needed)
# MAVRICK_DB_CONFIG = {
#     "server": r"YKE0-P19SP1301.fg.rbc.com\IN01",
#     "database": "DMAV_MAVRICK",
#     "username": "your_username",
#     "password": "your_password",
#     "driver": "ODBC Driver 17 for SQL Server",
#     "use_windows_auth": False,
#     "pool_size": 5
# }

# Usage example:
# from utils import DBManager
# from config import MAVRICK_DB_CONFIG
# 
# db = DBManager(**MAVRICK_DB_CONFIG)
