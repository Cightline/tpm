import libtorrent, cPickle, os, ConfigParser, json, optparse, cStringIO
from twisted.internet import reactor
from twisted.spread import pb, jelly
from twisted.python import util

def main():
    cfg = ConfigParser.RawConfigParser()
    cfg.readfp(open(os.path.expanduser("~/.tpm/config")))
    factory = pb.PBClientFactory()
    reactor.connectTCP(cfg.get("json_server", "address"), int(cfg.get("json_server", "port")), factory)
    factory.getRootObject().addCallback(tpm)
    reactor.run()


class tpm():
    def __init__(self, obj):
	self.obj = obj
	cfg = ConfigParser.RawConfigParser()
	if self.check_config:
	    cfg.readfp(open(os.path.expanduser("~/.tpm/config")))
	    self.ports = cfg.get("tracker", "ports")
	    self.tracker = cfg.get("tracker", "tracker")
	    self.json_server = cfg.get("json_server", "address")
	    self.json_port = cfg.get("json_server", "port")
	    #print "Config loaded"
    
	    
	parser = optparse.OptionParser()
	
	
	parser.add_option('-u', '--update',
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
		
	(self.options, self.args) = parser.parse_args()
	
	#now setup the session
	
	self.todo = []
	self.s = libtorrent.session()
	self.s.listen_on(int(self.ports.split(" ")[0]), int(self.ports.split(" ")[1]))
	#print "Using ports %s and %s for the tracker"  % (self.ports.split(" ")[0], self.ports.split(" ")[1])
	self.handle_args()
	
	
	
    
    
    def handle_args(self):
	if self.options.update_package_list:
	    self.todo += ["u"]
	    self.d_update_package_list()
	    
	if self.options.search_package:
	    self.todo += ["s"]
	    self.search_package(self.options.search_package)
	    
	if self.options.list_packages:
	    self.todo += ["l"]
	    self.list_packages()
	    
	
	
	

    
    
    def connectionMade(self):
	self.connected = 1
	print "Connection made to: %s" % self.json_server
	self.handle_args()
    	
	
    def connectionLost(self, reason):
	self.connected = 0
        print "Connection lost: %s" % reason
    
    
    
    def check_config(self):
	if os.path.exists(os.path.expanduser("~/.tpm/config")):
	    return True
	else:
	    print "You do not have a config file"
	    return False
    
    
    def check_done(self):
	if len(self.todo) == 0:
	    reactor.stop()
	    
	
    
    def upload_torrent(self, path):
	if self.connected:
	    if os.path.exists(path):
		tmp = open(path, "rb").read()
		self.transport.write(json.dumps(["upload", tmp]))
	    else:
		print "Cannot upload a file that does not exist"
	
    def create_package_torrent(self, file_path):
	fs = libtorrent.file_storage()
	libtorrent.add_files(fs, file_path)
	self.t = libtorrent.create_torrent(fs)
	self.t.add_tracker(self.tracker)
	self.t.set_creator("tpm 1.0")
	open("%s.torrent" % (self.t.generate()["info"]["name"]), "wb").write(libtorrent.bencode(self.t.generate()))
	
    def list_packages(self): #This is redundant, I will make a "package list loader"
	package_file = open(os.path.expanduser("~/.tpm/package_list"), "rb")
	packages = cPickle.load(package_file)
	for p in packages:
	    print p["name"]
	self.todo.remove("l")
	self.check_done()
	
    
    
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
	self.todo.remove("s")
	self.check_done()
	
    
    def format_list(self, data):
	package_file = open(os.path.expanduser("~/.tpm/package_list"),"wb")
	cPickle.dump(jelly.unjelly(data),package_file, 2)
	package_file.close()
	print "Packages updated"
	self.todo.remove("u")
	self.check_done()
	
    
    def d_update_package_list(self):
	print "Updating..."
	d_package_list = self.obj.callRemote("spew_package_list").addCallback(self.format_list)
	
    

    
main()
    
