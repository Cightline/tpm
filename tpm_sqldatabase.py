import sqlite3 as sql
import sqlite3.dbapi2 as dbapi
import os

#This import will handle all the lower level (not that Python is low level :D ) queries.

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        
	
	#Verify that the package list is there, if not create one.
	
	if os.path.exists(db_file):
	    try:
		self.connection = dbapi.connect(self.db_file, sql.PARSE_DECLTYPES)
		self.cursor = self.connection.cursor()
	    except:
		print "The local package database is corrupt, try tpm -u"
	else:
	    if raw_input("I could not find the package database, should I create one: ").lower().startswith("y"):
		try:
		    self.connection = dbapi.connect(self.db_file)
		    self.initilize_database()
		except:
		    print "I could not create the database"
	    else:
		print "I cannot do anything"
		exit()
		
	
    def initilize_database(self):
	self.cursor = self.connection.cursor()
	self.cursor.execute('''create table packages (name text, version text, location text)''')
	self.cursor.commit()
	print "Database initilized"
	
	
    def add_package(self, p_name, p_version, p_hash):
	#print "Adding package name: %s version: %s hash: %s " % (p_name, p_version, p_hash) #Make this a --verbose option
	self.cursor.execute("""insert into packages values (?,?,?)""", [p_name, p_version, p_hash]) 
	self.connection.commit()
	
    def remove_package(self):
	pass
	
	
    def update_package(self):
	pass



