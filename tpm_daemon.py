import libtorrent
import os 
import ConfigParser 
import json
import check_config
import tpm_sqldatabase as sql

from twisted.internet import reactor, protocol, defer
from twisted.protocols.basic import LineReceiver
from twisted.spread import jelly

class tpm_daemon():
    def __init__(self):
	self.daemon_config = "/etc/tpm/config"
	
	check_config.init_tpm()
	
	#Check the config, might make this a def.
	if check_config.check(self.daemon_config):
	    self.local_database = "/etc/tpm/torrent.db"
	    self.sql = sql.Database(self.local_database)
	    self.cfg = ConfigParser.RawConfigParser()
	    self.cfg.readfp(open(self.daemon_config))
	    self.ports = self.cfg.get("tracker", "ports")
	    self.tracker = self.cfg.get("tracker", "address")
	    self.server = self.cfg.get("server", "address")
	    self.s = libtorrent.session()
	    self.s.listen_on(int(self.ports.split(" ")[0]), int(self.ports.split(" ")[1]))
	    print "[tpmd] Running"
    
    
    
    #We pass the instances along to make things easier.
    def collect_server_object(self, instance):
	self.server_instance = instance 
    
    
    
    def collect_client_object(self, instance):
	self.client_instance = instance
    
    
    
    #Written to reduce extra code.
    def c_msg(self, message):
	self.client_instance.sendLine(json.dumps(message))
    
    
    
    def s_msg(self, message):
	self.server_instance.sendLine(json.dumps(message))
    
    
    
    #Connect to the server, creating this lets us only connect when its needed.
    def connect_server(self):
	try:
	    self.r_server = reactor.connectTCP(self.server, 8000, factory)
	    print "Connected to server"
	    return True
	except:
	    print "Could not connect to server"
    
    
    
    #We see if we are even connected to the server, then disconnect if so.
    def disconnect_server(self):
	
	if self.r_server:
	    try:
		self.r_server.disconnect()
		print "Disconnected from server"
		return True
	    except:
		print "Could not disconnect from server"
	else:
	    print "Cannot disconnect, not connected in the first place"


    
    #Here we actually do the searching for tpm, and transfer the found torrents back to it.
    def search_torrent(self, name):
	torrents = self.sql.return_packages()
	found = []
	if torrents:
	    for t in torrents:
		if name in t["name"]:
		    found.append(t["name"])
	    self.c_msg({"search":found})
	
	else:
	    self.c_msg({"search":None})
    
    
    
    #Not fully implemented
    def create_torrent(self, file_path):
	
	print "Creating .torrent for %s..." % file_path
	
	
	if os.path.exists(file_path):
	    fs = libtorrent.file_storage()
	    libtorrent.add_files(fs, str(file_path)) #Apparently file_path is unicode, and libtorrent does not like that. 
	    self.t = libtorrent.create_torrent(fs)
	    #self.t.add_tracker(self.tracker) tpm_daemon -> tpm_server -> opentracker
	    self.t.set_creator("tpmd 1.0")
	    torrent_name = self.t.generate()["info"]["name"]
	    with open("%s.torrent" % (torrent_name), "wb") as torrent_file:
		torrent_file.write(libtorrent.bencode(self.t.generate()))
	    print "Torrent %s created" % torrent_name
	    
	    #implement integrity check here
	    
	    return True
	
	else:
	    print "File does not exist"
	    
	
	
    #Torrent callback, (the user has responded).
    def torrent_largest_c(self, data):
	if data:
	    if self.create_torrent(self.largest):
		self.c_msg({"misc":"torrent_created"})
	
	#implement the rest
    
   
    
    #Torrent query 
    def torrent_largest_q(self, path):
	real_packages = {}
	largest = [None, 0]
	    
	for f in os.listdir(path):
	    size = os.path.getsize("%s/%s" % (path, f))
	    if size > largest[1]:
		largest[1] = size
		largest[0] = f
	
	self.largest = "%s/%s" % (path.rstrip("/"), largest[0].rstrip("/"))
	
	if self.largest not in self.sql.return_packages():
	    self.c_msg({"torrent_largest_q":[largest[0],largest[1]]}) 
	
	#implement else
   



    #This downloads the torrents from the server. It needs to be re-written, but this should do for now.
    def update_torrent_database(self):
	import urllib2 
    
	data = urllib2.urlopen("http://%s/tpm_server/torrent.db" % (self.server))
	
	if data.getcode() == 200:
	    data_length = data.info()["Content-Length"]
	    self.c_msg({"misc":"Downloading %s bytes" % (data_length)})
	    
	    if self.write_database(data.read(), True):
		self.sql.reload_database()
		return True, len(self.sql.return_packages())



	    
    def write_database(self, data, new_database=True):
	
	if new_database:
	    print "[tpmd] Writting new database"
	    with open(self.local_database, "wb") as new_database:
		new_database.write(data)
		return True
	
	print "[tpmd] Writting to existing database"
	with open(self.local_database, "ab") as new_database:
	    new_database.write(data)
	    return True
    
    
    
    #This handles the recieved data, and sends it to the appropriate function.
    def delegate_client_data(self, data, obj):
	print "recv_data", data
	data = json.loads(data)
	
	    
	if "search" in data.keys():
	    self.search_torrent(data["search"])
	    
	if "list" in data.keys():
	    self.sql.reload_database()
	    self.c_msg({"list":self.sql.return_pacakges()})
	    
	if "update_database" in data.keys():
	    self.c_msg({"update":self.update_torrent_database()})
	
	if "torrent_largest_c" in data.keys():
	    self.torrent_largest_c(data["torrent_largest_c"])
	
	if "torrent_largest" in data.keys():
	    self.torrent_largest_q(data["torrent_largest"])



#Protocol for the server
class Server_Proto(LineReceiver):
    
    def connectionMade(self):
	print "Connected to server"
	t.collect_server_object(self)
 
 
    def dataReceived(self, data):
	print "server_data", data 
	
    
	

#Protocol for the client (tpm)
class Client_Proto(LineReceiver):
    
    
    def connectionMade(self):
	print "Client connected"
	
	t.collect_client_object(self)
	
    def lineReceived(self, line):
	print "client_line", line
	t.delegate_client_data(line, self)

if __name__ == "__main__":
    check_config.check_root()
    t = tpm_daemon()
    factory = protocol.ClientFactory()
    d_factory = protocol.ServerFactory()
    factory.protocol = Server_Proto
    d_factory.protocol = Client_Proto
    reactor.listenTCP(8001, d_factory)
    reactor.run()
	
	


