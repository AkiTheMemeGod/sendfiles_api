import sqlite3 as sq
import base64

class Database:
    def __init__(self):
        self.connection = sq.connect("files.db", check_same_thread=False)
        self.init_db()

    def init_db(self):
        with self.connection as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    filedata BLOB NOT NULL
                )
            ''')
            conn.commit()

    def send_files(self, key, filename, filedata):
        with self.connection as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO files (key, filename, filedata) VALUES (?, ?, ?)",
                (key, filename, filedata)
            )
            conn.commit()

    def vacuum(self):
        cursor = self.connection.cursor()
        cursor.execute("vacuum")
        self.connection.close()

    def get_files(self, key):
        with self.connection as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, filedata FROM files WHERE key = ?", (key,))
            files = cursor.fetchall()
            result = []
            for file in files:
                if file[1].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    file_data_base64 = base64.b64encode(file[2]).decode('utf-8')
                    result.append((file[0], file[1], file_data_base64))
                else:
                    result.append((file[0], file[1], None))
            return result

    def get_file_data(self, file_id):
        with self.connection as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filename, filedata FROM files WHERE id = ?", (file_id,))
            file = cursor.fetchone()
            if file:
                filename, filedata = file
                return filename, filedata  # Return raw binary data
            return None

    def delete_file(self, file_id):
        with self.connection as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
            conn.commit()
