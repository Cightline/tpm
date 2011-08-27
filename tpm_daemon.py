from twisted.internet import reactor 
import check_config, libtorrent, os, ConfigParser
from twisted.protocols import basic
from twisted.internet import protocol
from twisted.application import service, internet

class tpm_daemon(protocol.Protocol):
    def __init__(self):
	self.daemon_config = "/home/stealth/.tpm/config"
	
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
	
	    
    def lineReceived(self, line):
	print "[Recv] ", line  
	    
    
    def connectionLost(self, reason):
	print "Connection lost ", reason
	
	
    def lineReceived(self, line):
	print "received", repr(line)
	
    def sendMessage(self, message):
	self.transport.write(message+"\n")
    
    
    def upload_torrent(self, path):
	if os.path.exists(path):
	    tmp = open(path, "rb").read()
	    #call remote upload
	else:
	    print "Cannot upload a file that does not exist"

    def create_package_torrent(self, file_path):
	fs = libtorrent.file_storage()
	libtorrent.add_files(fs, file_path)
	self.t = libtorrent.create_torrent(fs)
	self.t.add_tracker(self.tracker)
	self.t.set_creator("tpm 1.0")
	open("%s.torrent" % (self.t.generate()["info"]["name"]), "wb").write(libtorrent.bencode(self.t.generate()))


    

factory = protocol.ServerFactory()
factory.protocol = tpm_daemon
reactor.listenTCP(8001,factory)
reactor.run()




