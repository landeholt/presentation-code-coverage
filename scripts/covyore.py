from pathlib import Path
import sqlite3

class DB:
    def __init__(self, datafile: str = ".covyoredata") -> None:
        file_ = Path(__file__) / Path(datafile)
        new_db = not file_.exists()
        
        connection = sqlite3.connect(file_)
        self.con = connection
        
        if new_db:
            self.init_table()
        
    
    def init_table(self):
        
        connection = self.con
        connection.execute("CREATE TABLE hashes (hashid TEXT PRIMARY KEY, coverage REAL)")
        
    def insert_coverage(self, hashid: str, coverage: float):
        with self.con as con:
            cursor = con.cursor()
            
            cursor.execute(
                """
                INSERT OR REPLACE INTO hashes
                (hashid, coverage)
                VALUES (?,?)
                """,
                (hashid, coverage))
    
    def select_last_coverage(self, hashid: str):
        with self.con as con:
            cursor = con.cursor()
            
            return cursor.execute("SELECT coverage FROM hashes WHERE hashid=?", (hashid))
    def __enter__(self):
        self.con = self.con.__enter__()
        return self
    
    def __exit__(self, *args, **kwargs):
        self.con.__exit__(*args, **kwargs)
    

class Manager:
    
    def __init__(self):
        pass
    
    