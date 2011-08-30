import Pyro.core, libtorrent, os, ConfigParser, check_config

class tpm_daemon(Pyro.core.ObjBase):
    def __init__(self):
	Pyro.core.ObjBase.__init__(self)
	self.daemon_config = "/etc/tpm/config"
	
	check_config.init_tpm()
	
	
	if check_config.check(self.daemon_config):
	    self.cfg = ConfigParser.RawConfigParser()
	    self.cfg.readfp(open(self.daemon_config))
	    self.connect_server() 
	    self.ports = self.cfg.get("tracker", "ports")
	    self.tracker = self.cfg.get("tracker", "address")
	    self.s = libtorrent.session()
	    self.s.listen_on(int(self.ports.split(" ")[0]), int(self.ports.split(" ")[1]))
	    print "[tpmd] Running"
    
    
    def return_type(self):
	return "tpmd"
    
    def connect_server(self): #It will not stay connected to the server through out its lifetime, this is just temporary for debugging
	self.daemon = Pyro.core.getProxyForURI("PYROLOC://%s:7767/tpm_server" % (self.cfg.get("server", "address")))
	c_type = self.daemon.return_type()
	if c_type == "tpm_server":
	    print "[tpmd] Connected to server"
	    return True
	else:
	    print "Server returned wrong type %s" % c_type
	
	
    
    def upload_torrent(self, path):
	if os.path.exists(path):
	    if self.daemon.self.d(os.path.basename(path)) == False:
		if self.create_package_torrent(path):
		    self.daemon.announce_new_package(os.path.basename(path))
		    print "New torrent announced"
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


check_config.check_root()
	
Pyro.core.initServer()
daemon=Pyro.core.Daemon()
uri = daemon.connect(tpm_daemon(), "tpm_daemon")
open("/etc/tpm/d_port",'w').write(str(daemon.port))
print "Port: %s URI: %s" % (daemon.port, uri)
daemon.requestLoop()


	
	


