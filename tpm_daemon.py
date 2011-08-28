import Pyro.core, libtorrent, os, ConfigParser, check_config

class tpm_daemon(Pyro.core.ObjBase):
    def __init__(self):
	Pyro.core.ObjBase.__init__(self)
	self.daemon_config = "/etc/tpm/config"
	
	if os.getuid() != 0:
	    print "Run me as root" 
	    try:
		reactor.stop()
	    except:
		pass
	    exit()
	
	if check_config.check(self.daemon_config):
	    self.cfg = ConfigParser.RawConfigParser()
	    self.cfg.readfp(open(self.daemon_config))
	    self.ports = self.cfg.get("tracker", "ports")
	    self.daemon = Pyro.core.getProxyForURI("PYROLOC://%s:7766/tpm_server" % (self.cfg.get("server", "address")))
	    self.tracker = self.cfg.get("tracker", "tracker")
	    self.s = libtorrent.session()
	    self.s.listen_on(int(self.ports.split(" ")[0]), int(self.ports.split(" ")[1]))
	    print "Running"
	
    
    def upload_torrent(self, path):
	if os.path.exists(path):
	    tmp = open(path, "rb").read()
	    if self.create_package_torrent(path):
		pass #implement this
	else:
	    return "Cannot upload a file that does not exist"
	
    def create_package_torrent(self, file_path):
	print "Creating .torrent for %s..." % file_path
	fs = libtorrent.file_storage()
	libtorrent.add_files(fs, file_path)
	self.t = libtorrent.create_torrent(fs)
	self.t.add_tracker(self.tracker)
	self.t.set_creator("tpm 1.0")
	torrent_name = self.t.generate()["info"]["name"]
	open("%s.torrent" % (torrent_name), "wb").write(libtorrent.bencode(self.t.generate()))
	print "Torrent %s created" % torrent_name
	return True



Pyro.core.initServer()
daemon=Pyro.core.Daemon()
uri = daemon.connect(tpm_daemon(), "tpm_daemon")
#print "Port: %s URI: %s" % (daemon.port, uri)
daemon.requestLoop()


	
	


