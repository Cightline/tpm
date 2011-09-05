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
    
    
    def collect_server_object(self, instance):
	self.server_instance = instance 
    
    def check_torrent_exists(self, name):
	d = defer.Deferred()
	send_data = {}
	self.name = name
	print "Checking if package torrent %s exists server side..." % name
	send_data["check_exists"] = self.name
	print "send_data", send_data
	self.transport.write(json.dumps(send_data))
	return d
	

	
    def create_package_torrent(self, file_path):
	#if os.path.exists(path):
	#    if self.create_package_torrent(path):
	#	pass #implement
	#    else:
	#	print "Torrent already exists"
	#else:
	#    print "No such path"
	#
	print "Creating .torrent for %s..." % file_path
	fs = libtorrent.file_storage()
        if os.path.exists(file_path):
            print "Path %s does not exists." % file_path
            return False

        libtorrent.add_files(fs, file_path)
	self.t = libtorrent.create_torrent(fs)
	#self.t.add_tracker(self.tracker)
	self.t.set_creator("tpmd 1.0")
	torrent_name = self.t.generate()["info"]["name"]
	with open("%s.torrent" % (torrent_name), "wb") as torrent_file:
            torrent_file.write(libtorrent.bencode(self.t.generate()))
	print "Torrent %s created" % torrent_name
	return True
    
    def delegate_client_data(self, data, obj):
	print "recv_data", data
	data = json.loads(data)
	
	
	if "upload_package" in data.keys():
	    self.validate_torrent(data["upload_package"], obj)
	
	
    def lineReceived(self, line):
	print "line", line
    
    
    
class Server_Proto(protocol.Protocol):
    
    def connectionMade(self):
	print "Connected to server"
	t.collect_server_object(self)
 
 
    def dataReceived(self, data):
	print "server_data", data 
	


class Client_Proto(protocol.Protocol):
    
    def connectionMade(self):
	print "Client connected"
	
    def dataReceived(self, data):
	print "client_data", data
	t.delegate_client_data(data, self)
	


if __name__ == "__main__":
    check_config.check_root()
    t = tpm_daemon()
    factory = protocol.ClientFactory()
    d_factory = protocol.ServerFactory()
    factory.protocol = Server_Proto
    d_factory.protocol = Client_Proto
    reactor.listenTCP(8001, d_factory)
    reactor.connectTCP("localhost", 8000, factory)
    reactor.run()
	
	


