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
		print "Loaded package database"
		self.cursor = self.connection.cursor()
	    except:
		print "There is a error in the package database, aborting"
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
		
	#self.add_package("dummy_package1", 1.0, "2394902340293j3kl4j23490")
	#self.add_package("dummy_package2", 1.33, "3902099090902390239023")
	
    def initilize_database(self):
	self.cursor = self.connection.cursor()
	self.cursor.execute('''create table packages (name text NOT NULL UNIQUE COLLATE NOCASE, version text NOT NULL UNIQUE COLLATE NOCASE , hash text NOT NULL UNIQUE COLLATE NOCASE)''')
	self.cursor.commit()
	print "Database initilized"
	
    def return_packages(self): #I know this is not the best way to do this...
	print "[sql] Retriving packages"
	packages = []
	for p in self.cursor.execute('select * from packages order by name'):
	    packages += [{"name":p[0], "version":p[1], "hash":p[2]}]
	return packages 
	
	
	
    def add_package(self, p_name, p_version, p_hash):
	print "Adding package name: %s version: %s hash: %s " % (p_name, p_version, p_hash)
	
	self.cursor.execute("""insert into packages values (?,?,?)""", [p_name, p_version, p_hash]) 
	
	self.connection.commit()
	print "Package added"
	
    def remove_package(self):
	pass
	
	
    def update_package(self):
	pass


