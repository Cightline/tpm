import cPickle, os, ConfigParser, json, optparse, cStringIO, check_config, tpm_sqldatabase as sql
from twisted.internet import reactor
from twisted.spread import pb, jelly
from twisted.python import util    
import communicate


    


class tpm():
    def __init__(self, obj):
	self.obj = obj
	#Check to see if our config exists, then grab some args.
	if check_config.check("~/.tpm/config"):
	    cfg = ConfigParser.RawConfigParser()
	    cfg.readfp(open(os.path.expanduser("~/.tpm/config")))
	    self.json_server = cfg.get("json_server", "address")
	    self.json_port = cfg.get("json_server", "port")
	    self.sql = sql.Database(os.path.expanduser("~/.tpm/package.db"))
	    self.chunk_local = 0,10
	    self.chunk_size = int(cfg.get("json_server", "chunk_size"))
	    self.total = 0
	    communicate.run()
	    self.comm = communicate.Communicate()
	    
	#Setup our command line options
	parser = optparse.OptionParser()
	
	
	parser.add_option('-U', '--update',
				action="store_true",
				dest='update_package_list', 
				help="Update your local package list", 
			)
			
	parser.add_option('-S', '--search',
				action="store",
				dest="search_package",
				help="Search for a package",
			)
			
	parser.add_option('-l', '--list',
				action="store_true",
				dest="list_packages",
				help="List packages"
			)
	
	parser.add_option('-u', '--upload',
				action="store",
				dest="upload_package",
				help="tpm -u [package], used to manually upload a package torrent for testing"
				
			)
	(self.options, self.args) = parser.parse_args()
	
	
	
	self.handle_args()
	    
    
    def check_done(self):
	if reactor.running:
	    #It seems to throw a error, regardless of what you do, I'm thinking its something to do with the async properties it has. 
	    try:
		reactor.stop()
	    except:
		pass
	else:
	    exit()
	
	
	#This is redundant, I will make a "package list loader"
    def list_packages(self): 
	for p in self.sql.return_packages():
	    print p["name"]

	self.check_done()
	
	
	#This is redundant, I will make a "package list loader"
    def search_package(self, search):
	self.found = 0
	print "Searching..."
	for p in sql.return_packages():
	    if search == p["name"]:
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
    
    
    def deal_with_list(self, *args):
	if args[0][-1]:
	    package_length = args[0][-1]
	
	if args[0]:
	    data = args[0][0]
	    total_added, total = self.add_to_local(data)
	    self.chunk_local = self.total, self.total+self.chunk_size
	
	#print package_length
	#print "Total added : %s Total: %s " % (self.total, package_length)
	print "%s%%" % (int(round((self.total / float(package_length)) * 100)))
	
	if self.total == package_length:
	    print "Done, updated %s packages" % self.total
	    return self.check_done()
	
	self.obj.callRemote("spew_package_list", self.chunk_local).addCallback(self.deal_with_list)
	
	
	
	
	#This calls the "remote" function on the Json_Server
    def d_update_package_list(self):
	print "Updating..."
	self.obj.callRemote("spew_package_list", self.chunk_local, True).addCallback(self.deal_with_list)
	
	
    def handle_args(self):
	if self.options.update_package_list:
	    self.d_update_package_list()
	    
	elif self.options.search_package:
	    self.search_package(self.options.search_package.lower())
	    
	elif self.options.list_packages:
	    self.list_packages()
	    
	elif self.options.upload_package:
	    self.comm.sendMessage(json.dumps({"upload_torrent":self.options.upload_package}))
	
    

    
cfg = ConfigParser.RawConfigParser()
cfg.readfp(open(os.path.expanduser("~/.tpm/config")))
factory = pb.PBClientFactory()
reactor.connectTCP(cfg.get("json_server", "address"), int(cfg.get("json_server", "port")), factory)
factory.getRootObject().addCallback(tpm)
reactor.run()
    
