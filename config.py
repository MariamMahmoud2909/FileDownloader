# Database Configurations

DB_CONFIG = {
    'server': 'DESKTOP-OAE4SOD',
    'database': 'FileDownloader',
    'username': 'DESKTOP-OAE4SOD\\Ahmed',
    'password': '123',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

CONNECTION_STRING = (
    f"DRIVER={DB_CONFIG['driver']};"
    f"SERVER={DB_CONFIG['server']};"
    f"DATABASE={DB_CONFIG['database']};"
    f"Trusted_Connection=yes;"  
)