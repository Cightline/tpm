
import os, json, ConfigParser, sqldatabase
from twisted.internet import reactor
from twisted.spread import pb, jelly

class Json_Server(pb.Root):
    def __init__(self):
	cfg = ConfigParser.RawConfigParser()
	cfg.readfp(open(os.path.expanduser("~/.tpm_server/config")))
	
	self.package_file = cfg.get("package", "dir")
	self.sql = sqldatabase.Database(self.package_file)
	    
	    
	
	
    def invalidate_package_torrent(self, torrent):
	pass 
	
	
	
	
    #Remotes 
    
    	
    def remote_spew_package_list(self): #This is gonna be poorly written until I figure something out
	packages = []
	#return json.dumps({"package_list":[self.sql.return_packages()]}
	return jelly.jelly(self.sql.return_packages())
    
    def remote_announce_new_package(self):
	pass 
    





if __name__ == "__main__":
    reactor.listenTCP(8000, pb.PBServerFactory(Json_Server()))
    reactor.run()
