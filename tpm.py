import libtorrent, cPickle, os, ConfigParser
from twisted.internet import reactor, protocol


class tpm(protocol.Protocol):
    def __init__(self):
	cfg = ConfigParser.RawConfigParser()
	if self.check_config:
	    cfg.readfp(open(os.path.expanduser("~/.tpm/config")))
	    self.ports = cfg.get("tracker", "ports")
	    self.tracker = cfg.get("tracker", "tracker")
	    self.json_server = cfg.get("json_server", "address")
	    self.json_port = cfg.get("json_server", "port")
	    print "Config loaded"
	
	self.connected = 0
	self.s = libtorrent.session()
	self.s.listen_on(int(self.ports.split(" ")[0]), int(self.ports.split(" ")[1]))
	print "Using ports %s and %s for the tracker"  % (self.ports.split(" ")[0], self.ports.split(" ")[1])
	self.create_package_torrent()
	
    
    def connectionMade(self):
	self.connected = 1
	print "Connection made to: %s" % self.json_server
    
    def dataReceived(self, data):
        #"As soon as any data is received, write it back."
        #print "Server said:", data
        #self.transport.loseConnection()
	print "Data: %s " % data
	
	
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
		self.transport.write(json.dumps(["upload", tmp]) 
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
	
    
class EchoFactory(protocol.ClientFactory):
    protocol = tpm

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        reactor.stop()
    
	
if __name__ == "__main__":
    cfg = ConfigParser.RawConfigParser()
    cfg.readfp(open(os.path.expanduser("~/.tpm/config")))
    json_server = cfg.get("json_server", "address")
    json_port = cfg.get("json_server", "port")
   
    f = EchoFactory()
    reactor.connectTCP(json_server, int(json_port), f)
    reactor.run()
