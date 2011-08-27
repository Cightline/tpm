import Pyro.core, check_config, libtorrent, os, ConfigParser



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
	    cfg = ConfigParser.RawConfigParser()
	    cfg.readfp(open(self.daemon_config))
	    self.ports = cfg.get("tracker", "ports")
	    self.tracker = cfg.get("tracker", "tracker")
	    self.s = libtorrent.session()
	    self.s.listen_on(int(self.ports.split(" ")[0]), int(self.ports.split(" ")[1]))
	    print "Running"
	
	    
    
    def upload_torrent(self, path):
	if os.path.exists(path):
	    tmp = open(path, "rb").read()
	    self.create_package_torrent(path)
	    return "Handling package"
	else:
	    return "Cannot upload a file that does not exist"
	    
    def create_package_torrent(self, file_path):
	print "Creating .torrent for %s..." % file_path
	fs = libtorrent.file_storage()
	libtorrent.add_files(fs, file_path)
	self.t = libtorrent.create_torrent(fs)
	self.t.add_tracker(self.tracker)
	self.t.set_creator("tpm 1.0")
	open("%s.torrent" % (self.t.generate()["info"]["name"]), "wb").write(libtorrent.bencode(self.t.generate()))
	print "Torrent created"

Pyro.core.initServer()
daemon=Pyro.core.Daemon()
uri = daemon.connect(tpm_daemon(), "tpm_daemon")
print "Port: %s URI: %s" % (daemon.port, uri)
daemon.requestLoop()




