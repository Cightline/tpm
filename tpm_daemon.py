import libtorrent, os, ConfigParser, json, check_config
from twisted.internet import reactor, protocol, defer
from twisted.spread import jelly

class tpm_daemon(protocol.Protocol):
    def __init__(self):
	self.daemon_config = "/etc/tpm/config"
	
	check_config.init_tpm()
	
	
	if check_config.check(self.daemon_config):
	    self.cfg = ConfigParser.RawConfigParser()
	    self.cfg.readfp(open(self.daemon_config))
	    self.ports = self.cfg.get("tracker", "ports")
	    self.tracker = self.cfg.get("tracker", "address")
	    self.sql = sql.Database("/etc/tpm/package.db")
	    self.s = libtorrent.session()
	    self.s.listen_on(int(self.ports.split(" ")[0]), int(self.ports.split(" ")[1]))
	    print "[tpmd] Running"
    
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
	
    def d_update_package_list(self):
	print "Updating..."
	import urllib2
	open("/etc/tpm/package.db", "wb").write(urllib2.urlopen("http://%s/tpm_server/package.db" % (self.json_server)).read())
	self.sql = sql.Database("/etc/tpm/package.db")
	print "Done, retrieved %s packages" % (len(self.sql.return_packages()))
	self.check_done()

    def add_to_local(self, data):
	total_added = 0 
	total = len(data)
	for package in data:
	    self.sql.add_package(package["name"], package["version"], package["hash"])
	    total_added += 1
	
	self.total += total_added
	return total_added, total


    def check_torrent_exists(self, name):
	d = defer.Deferred()
	send_data = {}
	self.name = name
	print "Checking if package torrent %s exists server side..." % name
	send_data["check_exists"] = self.name
	print "send_data", send_data
	self.transport.write(json.dumps(send_data))
	return d
    
    def upload_torrent(self, path):
	if os.path.exists(path):
	    if self.create_package_torrent(path):
		pass #implement
	    else:
		print "Torrent already exists"
	else:
	    print "No such path"
	
    def create_package_torrent(self, file_path):
	print "Creating .torrent for %s..." % file_path
	fs = libtorrent.file_storage()
        if os.path.exists(file_path):
            print "Path %s does not exists." % file_path
            return False

        libtorrent.add_files(fs, file_path)
	self.t = libtorrent.create_torrent(fs)
	self.t.add_tracker(self.tracker)
	self.t.set_creator("tpmd 1.0")
	torrent_name = self.t.generate()["info"]["name"]
	with open("%s.torrent" % (torrent_name), "wb") as torrent_file:
            torrent_file.write(libtorrent.bencode(self.t.generate()))
	print "Torrent %s created" % torrent_name
	return True
    
    def delegate_data(self, data):
	print "recv_data", data
	data = json.loads(data)
	
	if self.name in data:
	    print "Torrent %s = %s" % (self.name, data[self.name])
	    self.upload_torrent(self.file_path)
	
	
    def lineReceived(self, line):
	print "line", line
    
    
    
    ##Twisted
    
    def connectionMade(self):
	print "Connected"

    def dataReceived(self, data):
	self.delegate_data(data)
	
    def lineReceived(self, line):
	self.delegate_data(data)
 

class Daemon_Proto(protocol.Protocol):
    
    def connectionMade(self):
	print "someone connected"
	
    def dataReceived(self, data):
	print "s_data", data
	
    def lineReceived(self, line):
	print "s_line", line

if __name__ == "__main__":
    check_config.check_root()
    factory = protocol.ClientFactory()
    d_factory = protocol.ServerFactory()
    factory.protocol = tpm_daemon
    d_factory.protocol = Daemon_Proto
    reactor.listenTCP(8001, d_factory)
    reactor.connectTCP("localhost", 8000, factory)
    reactor.run()
	
	


