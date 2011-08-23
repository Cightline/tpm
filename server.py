
import os, json, ConfigParser, sqldatabase, cStringIO
from twisted.internet import reactor, interfaces 
from twisted.spread import pb, jelly
from twisted.spread.util import FilePager
	


class Json_Server(pb.Root):
    def __init__(self):
	#Load up the server conifg.
	cfg = ConfigParser.RawConfigParser()
	cfg.readfp(open(os.path.expanduser("~/.tpm_server/config")))
	self.package_file = cfg.get("package", "dir")
	self.sql = sqldatabase.Database(self.package_file)
    
	#This function will tell the tracker that the package/torrent is invalid. 
    def invalidate_package_torrent(self, torrent):
	pass 
	
	
	
	
    #This remote function returns the package list to the client.
    def remote_spew_package_list(self): #This is gonna be poorly written until I figure something out
	print "[Server] Spewing..."
	return jelly.jelly(self.sql.return_packages())
	    
	
    #This is for when a client creates (automatically) a new package torrent that does not already exist.
    def remote_announce_new_package(self):
	pass 
    





if __name__ == "__main__":
    reactor.listenTCP(8000, pb.PBServerFactory(Json_Server()))
    reactor.run()
