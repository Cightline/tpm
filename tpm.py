import libtorrent, cPickle, os, ConfigParser, json, optparse
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
	    print "Config loaded"
    
	    
	parser = optparse.OptionParser()
	
	
	parser.add_option('-u', '--update',
				action="store_true",
				dest='update_package_list', 
				help="Update your local package list", 
			)
		
	(self.options, self.args) = parser.parse_args()
	
	#now setup the session
	
	self.connected = 0
	self.s = libtorrent.session()
	self.s.listen_on(int(self.ports.split(" ")[0]), int(self.ports.split(" ")[1]))
	print "Using ports %s and %s for the tracker"  % (self.ports.split(" ")[0], self.ports.split(" ")[1])
	self.handle_args()
	
	
	
    
    
    def handle_args(self):
	if self.options.update_package_list:
	    self.d_update_package_list()
	

    
    
    def connectionMade(self):
	self.connected = 1
	print "Connection made to: %s" % self.json_server
	self.handle_args()
    
    def dataReceived(self, data):
	print "Data: %s " % data
	
	json_data = json.loads(data)
	
	

	
	
    def connectionLost(self, reason):
	self.connected = 0
        print "Connection lost: %s" % reason
    
    
    
    def check_config(self):
	if os.path.exists(os.path.expanduser("~/.tpm/config")):
	    return True
	else:
	    print "You do not have a config file"
	    return False
    
    
    
	
    
    def upload_torrent(self, path):
	if self.connected:
	    if os.path.exists(path):
		tmp = open(path, "rb").read()
		self.transport.write(json.dumps(["upload", tmp]))
	    else:
		print "Cannot upload a file that does not exist"
	
    def create_package_torrent(self):
	fs = libtorrent.file_storage()
	libtorrent.add_files(fs, "/home/stealth/Desktop/test_torrent")
	self.t = libtorrent.create_torrent(fs)
	self.t.add_tracker(self.tracker)
	self.t.set_creator("tpm 1.0")
	open("%s.torrent" % (self.t.generate()["info"]["name"]), "wb").write(libtorrent.bencode(self.t.generate()))
	
    def search_package(self, package):
	if self.connected:
	    self.transport.write(json.dumps({"search":package}))
    
    def update_package_list(self, obj):
	print jelly.unjelly(obj)
    
    def d_update_package_list(self):
	d_package_list = self.obj.callRemote("spew_package_list")
	d_package_list.addCallbacks(self.update_package_list)
    

    
main()
    
