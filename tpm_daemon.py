import libtorrent, os, ConfigParser, json, check_config, tpm_sqldatabase as sql
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
	    self.server = self.cfg.get("server", "address")
	    self.sql = sql.Database("/etc/tpm/torrent.db")
	    self.s = libtorrent.session()
	    self.s.listen_on(int(self.ports.split(" ")[0]), int(self.ports.split(" ")[1]))
	    print "[tpmd] Running"
    
    
    def collect_server_object(self, instance):
	self.server_instance = instance 
    
    def collect_client_object(self, instance):
	self.client_instance = instance
    
    def c_msg(self, message):
	self.client_instance.transport.write(json.dumps(message))
	
    def s_msg(self, message):
	self.server_instance.transport.write(json.dumps(message))
	
    def connect_server(self):
	try:
	    self.r_server = reactor.connectTCP(self.server, 8000, factory)
	    print "Connected to server"
	    return True
	except:
	    print "Could not connect to server"
	
    def disconnect_server(self):
	try:
	    self.r_server.disconnect()
	    print "Disconnected from server"
	    return True
	except:
	    print "Could not disconnect from server"
    
    
    def list_torrents(self):
	packages = self.sql.return_packages()
	    
	if packages:
	    self.c_msg({"list":packages})
    
	else:
	    self.c_msg({"list":None})
    
    
    
	
    def create_package_torrent(self, file_path):
	
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
    
    def search_torrent(self, name):
	torrents = self.sql.return_packages()
	
	if torrents:
	    self.c_msg({"search":torrents})
	else:
	    self.c_msg({"search":None})
    
    
    def update_torrent_database(self):
	import urllib2 
	
	try:
	    new_packages = urllib2.urlopen("http://%s/tpm_server/torrent.db" % (self.server)).read()
	    
	    with open("/etc/tpm/torrent.db", "wb") as local_torrent_database:
		local_torrent_database.write(new_packages)
	    return True
	    
	except:
	    pass 
	
    
    def delegate_client_data(self, data, obj):
	print "recv_data", data
	data = json.loads(data)
	
	
	if "upload" in data.keys():
	    self.validate_torrent(data["upload_package"], obj)
	    
	if "search" in data.keys():
	    self.search_torrent(data["search"])
	    
	if "list" in data.keys():
	    self.list_torrents()
	    
	if "update_torrents" in data.keys():
	    
	    if self.update_torrent_database():
		self.c_msg(json.dumps({"success":"update_database"}))
	    else:
		self.c_msg(json.dumps({"error":"update_database"}))
		
	    

    
class Server_Proto(protocol.Protocol):
    
    def connectionMade(self):
	print "Connected to server"
	t.collect_server_object(self)
 
 
    def dataReceived(self, data):
	print "server_data", data 
	


class Client_Proto(protocol.Protocol):
    
    def connectionMade(self):
	print "Client connected"
	t.collect_client_object(self)
	
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
    reactor.run()
	
	


