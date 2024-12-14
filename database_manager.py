import pyodbc
from threading import Lock

class DatabaseManager:
    #Handles all database-related operations for managing file downloads
    
    def __init__(self, connection_string):
        self.connection = pyodbc.connect(connection_string)
        self.lock = Lock() #synchronizes access to the database, ensuring that only one thread interacts with the database at a time.
        self.create_tables()
    
    def connect(self):
        """Reconnects to the database if the connection is lost or closed."""
        if not self.connection:
            self.connection = pyodbc.connect(self.connection_string)

    def close(self):
        """Closes the database connection and sets the connection to None."""
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def create_tables(self):
        """Ensures that the Downloads table exists in the database before any operations are performed."""
        with self.connection.cursor() as cursor: # Use a context manager to create a cursor object for executing SQL commands.
            cursor.execute("""
            if not exists (select * from sys.tables WHERE name = 'Downloads')
            begin
                create table Downloads (
                    id int identity primary key,
                    url nvarchar(max) not null,
                    status nvarchar(50) not null,
                    file_path nvarchar(max),
                    retry_count int default 3
                )
            end
        """)
            self.connection.commit()

    def add_download(self, url):
        """Adds a new download entry to the database with a "Pending" status."""
        with self.lock: #to prevent simultaneous writes to the database from multiple threads.
         with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO Downloads (url, status) VALUES (?, 'Pending')", url)
            self.connection.commit()

    def update_download(self, download_id, status, file_path=None, retry_count=None):
        """Updates the status, file path, or retry count for a specific download."""
        with self.connection.cursor() as cursor:
            query = "UPDATE Downloads SET status = ?, file_path = ?, retry_count = ? WHERE id = ?"
            cursor.execute(query, status, file_path, retry_count, download_id)
            self.connection.commit()
    
    def delete_download(self, download_id, status=None, file_path=None, retry_count=None):
        """Deletes a download entry from the database."""
        with self.connection.cursor() as cursor:
            query = "DELETE FROM downloads WHERE id = %s"
            cursor.execute(query, status, file_path, retry_count, download_id)
            self.connection.commit()
    
    def get_pending_downloads(self):
        """Retrieves all downloads that have a "Pending" status."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, url, retry_count FROM Downloads WHERE status = 'Pending'")
            return cursor.fetchall()

    def get_download_history(self):
        """Retrieves a history of completed, failed, or removed downloads."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT url, status, file_path FROM Downloads WHERE status IN ('Completed', 'Failed', 'Removed')")
            return cursor.fetchall()
