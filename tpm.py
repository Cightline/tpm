#!/usr/bin/env python2
import cPickle, os, ConfigParser, json, optparse, cStringIO, tpm_sqldatabase as sql, check_config, sys
from twisted.internet import reactor, defer, protocol
from twisted.python import util    


    


class tpm():
    def __init__(self):
	
	self.config = "/etc/tpm/config"
	
	#Check to see if our config exists, then grab some args.
	if check_config.check(self.config):
	    cfg = ConfigParser.RawConfigParser()
	    cfg.readfp(open(self.config))
	    self.json_server = cfg.get("server", "address")
	    self.json_port = cfg.get("server", "port")
	    self.sql = sql.Database("/etc/tpm/package.db")
	    self.daemon_port = open("/etc/tpm/d_port",'r').read()
	
	    
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
    
    def handle_instance(self, instance):
	self.instance = instance
	self.handle_args()
    
    def handle_args(self):
	
	if self.options.update_package_list:
	    self.d_update_package_list()
	    
	elif self.options.search_package:
	    self.search_package(self.options.search_package.lower())
	    
	elif self.options.list_packages:
	    self.list_packages()
	    
	elif self.options.upload_package:
	    self.instance.transport.write(json.dumps({"upload_package":self.options.upload_package}))
	
	elif self.options.package_manager:
	    pass
	    
	else:
	    print "No args"
	    exit()


class tpm_Proto(protocol.Protocol):
    def connectionMade(self):
	print "Connected to daemon"
	t.handle_instance(self)


if __name__ == "__main__":
    check_config.check_root()
    check_config.init_tpm()
    t = tpm()
    factory = protocol.ClientFactory()
    factory.protocol = tpm_Proto
    reactor.connectTCP("localhost", 8001, factory)
    reactor.run()
    


    
