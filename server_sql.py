import sqlite3 as sql
import sqlite3.dbapi2 as dbapi
import os

#This import will handle all the lower level (not that Python is low level :D ) queries.
#implement sig, server needs to have package sigs sent to it. 


class Database:
    def __init__(self, db_file):
        self.db_file = db_file
	
	#Verify that the package list is there, if not create one.
	
	if os.path.exists(db_file):
	    try:
		self.connection = dbapi.connect(self.db_file, sql.PARSE_DECLTYPES)
		print "[sqlite3] Loaded package database"
		self.cursor = self.connection.cursor()
	    except:
		print "There is a error in the package database, aborting"
	else:
	    if raw_input("I could not find the package database, should I create one: ").lower().startswith("y"):
		try:
		    self.connection = dbapi.connect(self.db_file)
		    self.initilize_database()
		except:
		    print "I could not create the database, does the directory %s need to be created?" % (self.db_file)
	    else:
		print "I cannot do anything"
		exit()
		
	
	
    def initilize_database(self):
	self.cursor = self.connection.cursor()
	self.cursor.execute('''create table packages (name text NOT NULL UNIQUE COLLATE NOCASE, version text NOT NULL COLLATE NOCASE , hash text NOT NULL COLLATE NOCASE, sig text NOT NULL COLLATE NOCASE)''')
	self.connection.commit()
	print "Database initilized"
	
    def return_packages(self): #I know this is not the best way to do this...
	print "[sqlite3] Gathered packages"
	packages = []
	for p in self.cursor.execute('select * from packages order by name'):
	    packages += [{"name":p[0], "version":p[1], "hash":p[2], "sig":p[3]}]
	return packages 
        
    def add_package(self, p_name, p_version, p_hash, p_sig):
        #print "Adding package name: %s version: %s hash: %s " % (p_name, p_version, p_hash)
	
	self.cursor.execute("""insert into packages values (?,?,?,?)""", [p_name, p_version, p_hash, p_sig]) 
            #self.cursor.execute("""UPDATE packages SET name=? AND version=? AND hash=?""", [p_name, p_version, p_hash])
        #except:
         #   print "[Package] %s NOT added" % p_name
          #  return False
        
        self.connection.commit()
        print "[Package] %s added" % p_name
        return True
        
    def remove_package(self):
        pass
        
        
    def update_package(self):
        pass


