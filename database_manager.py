import pyodbc

class DatabaseManager:
    
    def __init__(self, connection_string):
        self.connection = pyodbc.connect(connection_string)
        self.create_tables()
        
    def connect(self):
        if not self.connection:
            self.connection = pyodbc.connect(self.connection_string)

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def create_tables(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            if not exists (select * from sys.tables WHERE name = 'Downloads')
            begin
                create table Downloads (
                    id int identity primary key,
                    url nvarchar(max) not null,
                    status nvarchar(50) not null,
                    file_path nvarchar(max),
                    retry_count int default 0
                )
            end
        """)
            self.connection.commit()

    def add_download(self, url):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO Downloads (url, status) VALUES (?, 'Pending')", url)
            self.connection.commit()

    def update_download(self, download_id, status, file_path=None, retry_count=None):
        with self.connection.cursor() as cursor:
            query = "UPDATE Downloads SET status = ?, file_path = ?, retry_count = ? WHERE id = ?"
            cursor.execute(query, status, file_path, retry_count, download_id)
            self.connection.commit()
    
    def delete_download(self, download_id, status, file_path=None, retry_count=None):
        with self.connection.cursor() as cursor:
            query = "DELETE FROM downloads WHERE id = %s"
            cursor.execute(query, status, file_path, retry_count, download_id)
            self.connection.commit()
        #self.execute(query, (download_id,))
    
    def get_pending_downloads(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, url, retry_count FROM Downloads WHERE status = 'Pending'")
            return cursor.fetchall()

    def get_download_history(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT url, status, file_path FROM Downloads WHERE status IN ('Completed', 'Failed')")
            return cursor.fetchall()
