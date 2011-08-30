#!/usr/bin/env python2
import Pyro.core, cPickle, os, ConfigParser, json, optparse, cStringIO, tpm_sqldatabase as sql, check_config, sys
from twisted.internet import reactor, defer
from twisted.python import util    


    


class tpm():
    def __init__(self):
	
	
	check_config.init_tpm()
	self.config = "/etc/tpm/config"
	
	#Check to see if our config exists, then grab some args.
	if check_config.check(self.config):
	    cfg = ConfigParser.RawConfigParser()
	    cfg.readfp(open(self.config))
	    self.json_server = cfg.get("server", "address")
	    self.json_port = cfg.get("server", "port")
	    self.sql = sql.Database("/etc/tpm/package.db")
	    self.daemon_port = open("/etc/tpm/d_port",'r').read()
	    self.connect_daemon()
	else:
	    self.check_done()
	    
	#Setup our command line options
	parser = optparse.OptionParser()
	
	
	parser.add_option('--update',
				action="store_true",
				dest='update_package_list', 
				help="Update your local package list", 
			)
			
	parser.add_option('-s', '--search',
				action="store",
				dest="search_package",
				help="Search for a package",
			)
			
	parser.add_option('-l', '--list',
				action="store_true",
				dest="list_packages",
				help="List packages"
			)
	
	parser.add_option('--upload',
				action="store",
				dest="upload_package",
				help="tpm -u [package], used to manually upload a package torrent for testing"
				
			)
			
	parser.add_option('-p', '--package-manager',
				action="store",
				dest="package_manager",
				help="package manager hook"
			)
			
	(self.options, self.args) = parser.parse_args()
	
	
	
	self.handle_args()
	
    
    
    
    def connect_daemon(self): #It will not stay connected to the server through out its lifetime, this is just temporary for debugging
	self.daemon = Pyro.core.getProxyForURI("PYROLOC://localhost:%s/tpm_daemon" % self.daemon_port)
	c_type = self.daemon.return_type()
	if c_type == "tpmd":
	    print "[tpm] Connected to daemon"
	    return True
	else:
	    print "daemon returned wrong type %s" % c_type
    
    def check_done(self):
	if reactor.running:
	    #It seems to throw a error, regardless of what you do, I'm thinking its something to do with the async properties it has. 
	    try:
		reactor.stop()
	    except:
		pass
	else:
	    exit()
	
    def list_packages(self): 
	for p in self.sql.return_packages():
	    print p["name"]

	self.check_done()
	
	
	
    def search_package(self, search):
	self.found = 0
	print "Searching..."
	for p in self.sql.return_packages():
	    if search in p["name"]:
		self.found += 1
		print "[%s] version: %s " % (p["name"], p["version"])
		
	if self.found == 0:
	    print "Package not found"
	    
	self.check_done()
    
    def add_to_local(self, data):
	total_added = 0 
	total = len(data)
	for package in data:
	    self.sql.add_package(package["name"], package["version"], package["hash"])
	    total_added += 1
	
	self.total += total_added
	return total_added, total
	
	
	
    def d_update_package_list(self):
	print "Updating..."
	import urllib2
	open("/etc/tpm/package.db", "wb").write(urllib2.urlopen("http://%s/tpm_server/package.db" % (self.json_server)).read())
	self.sql = sql.Database("/etc/tpm/package.db")
	print "Done, retrieved %s packages" % (len(self.sql.return_packages()))
	self.check_done()
    
    def handle_args(self):
	
	if self.options.update_package_list:
	    self.d_update_package_list()
	    
	elif self.options.search_package:
	    self.search_package(self.options.search_package.lower())
	    
	elif self.options.list_packages:
	    self.list_packages()
	    
	elif self.options.upload_package:
	    print self.daemon.upload_torrent(self.options.upload_package)
	    self.check_done()
	
	elif self.options.package_manager:
	    
	    #self.daemon.upload_torrent(self.options.package_manager.replace(".part",""))
	    #print self.options.package_manager
	    #print "[sys] %s" % sys.argv
	    
	    if sys.argv[-1].split(".")[-1] == "db":
		#print "database %s" % sys.argv[-1]
		pass
	    else:
		local_path = sys.argv[2].replace(".part","")
		os.popen("/usr/bin/wget --passive-ftp -c -O %s %s" % (local_path, sys.argv[-1])) #(url, local path), Inefficent, will fix
		print "Sending %s to tpm_daemon [port %s]..." % (local_path, self.daemon_port) 
		self.daemon.upload_torrent(local_path)
	    
	    self.check_done()
	    
	else:
	    print "No args"
	    exit()



check_config.check_root()
tpm()
reactor.run()
    
