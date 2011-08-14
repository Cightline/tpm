import sqlite3 as sql
import sqlite3.dbapi2 as dbapi

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = dbapi.connect( self.db_file )
        self.cursor = self.connection.cursor()


