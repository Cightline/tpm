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
	    self.s = libtorrent.session()
	    self.s.listen_on(int(self.ports.split(" ")[0]), int(self.ports.split(" ")[1]))
	    print "[tpmd] Running"
    
    
    
    
    def check_torrent_exists(self, name):
	d = defer.Deferred()
	send_data = {}
	self.name = name
	print "Checking if package torrent %s exists server side..." % name
	send_data["check_exists"] = self.name
	print "send_data", send_data
	self.transport.write(json.dumps(send_data))
	return d
	
    
    def need_upload(self, path):
	if not path:
	    print "Uploading %s" % path
	    self.upload_torrent(path)
    
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
	libtorrent.add_files(fs, file_path)
	self.t = libtorrent.create_torrent(fs)
	self.t.add_tracker(self.tracker)
	self.t.set_creator("tpmd 1.0")
	torrent_name = self.t.generate()["info"]["name"]
	open("%s.torrent" % (torrent_name), "wb").write(libtorrent.bencode(self.t.generate()))
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
	
	


