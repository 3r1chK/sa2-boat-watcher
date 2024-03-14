# controller/DbManager.py
import sqlite3


class DbManager:

    def __init__(self, db_config):
        self.config = db_config
        self.conn = sqlite3.connect(self.config.get("sqlite3_path"))

    def __del__(self):
        self.conn.close()

    def is_initialized(self):
        return False
