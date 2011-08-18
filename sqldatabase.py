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
		self.connection = dbapi.connect(self.db_file)
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
		
	self.add_package("wat", "ok", "hur")
	
    def initilize_database(self):
	self.cursor = self.connection.cursor()
	self.cursor.execute('''create table packages (name text, version text, location text)''')
	print "Database initilized"
	
    def return_packages(self):
	print "Retriving packages"
	packages = self.cursor.execute('select * from packages order by name')
	for p in packages:
	    print p
	print type(packages)
	return packages
	
	
    def add_package(self, p_name, p_version, p_hash):
	print "Adding package ", p_name
	self.cursor.execute("""insert into packages values ('%s, %s, %s')""" % (p_name, p_version, p_hash)) #I don't think I'm supposed to do it this way
	print "Package added"
	
    def remove_package(self):
	pass
	
	
    def update_package(self):
	pass


