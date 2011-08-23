import cPickle, os, ConfigParser, json, optparse, cStringIO, check_config, tpm_sqldatabase as sql
from twisted.internet import reactor
from twisted.spread import pb, jelly
from twisted.python import util    


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
    
	#Setup our command line options
	parser = optparse.OptionParser()
	
	
	parser.add_option('-u', '--update',
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
	package_file = open(os.path.expanduser("~/.tpm/package_list"), "rb")
	packages = cPickle.load(package_file)
	for p in packages:
	    print p["name"]

	self.check_done()
	
	
	#This is redundant, I will make a "package list loader"
    def search_package(self, search):
	self.found = 0
	package_file = open(os.path.expanduser("~/.tpm/package_list"), "rb")
	packages = cPickle.load(package_file)
	print "Searching..."
	for p in packages:
	    if search == p["name"]:
		self.found += 1
		print "[%s] version: %s " % (p["name"], p["version"])
	if self.found == 0:
	    print "Package not found"
	    
	package_file.close()
	self.check_done()
	
	
	#This is redundant, I will make a "package list loader"
	
    def format_list(self, data):
	total = 0
	for p in jelly.unjelly(data):
	    self.sql.add_package(p["name"], p["version"], p["hash"])
	    total += 1
	print "Packages updated: [%s]" % total
	self.check_done()
	
	
	#This calls the "remote" function on the Json_Server
    def d_update_package_list(self):
	print "Updating..."
	self.obj.callRemote("spew_package_list").addCallback(self.format_list)
	
	
    def handle_args(self):
	if self.options.update_package_list:
	    self.d_update_package_list()
	    
	elif self.options.search_package:
	    self.search_package(self.options.search_package.lower())
	    
	elif self.options.list_packages:
	    self.list_packages()
	
	

    
cfg = ConfigParser.RawConfigParser()
cfg.readfp(open(os.path.expanduser("~/.tpm/config")))
factory = pb.PBClientFactory()
reactor.connectTCP(cfg.get("json_server", "address"), int(cfg.get("json_server", "port")), factory)
factory.getRootObject().addCallback(tpm)
reactor.run()
    
