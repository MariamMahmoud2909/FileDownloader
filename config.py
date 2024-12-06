# db configurations
DB_CONFIG = {
    'server': 'DESKTOP-9UUO4AR',
    'database': 'FileDownloader',
    'username': 'DESKTOP-9UU04AR\\MAKKA',
    'password': '',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

CONNECTION_STRING = (
    f"DRIVER={DB_CONFIG['driver']};"
    f"SERVER={DB_CONFIG['server']};"
    f"DATABASE={DB_CONFIG['database']};"
    f"Trusted_Connection=yes;"  
)