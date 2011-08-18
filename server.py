
import os, json, ConfigParser
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory


class Json_Server():
    def __init__(self):
	cfg = ConfigParser.RawConfigParser()
	cfg.readfp(open(os.path.expanduser("~/.tpm_server/config")))
	
	self.package_file = cfg.get("package", "dir")
	if os.path.exists(self.package_file):
	    print "Loading package file..."
	    
	else:
	    print "I did not load the package file"
	    
	    
	    
    def recieve_package(self):
	pass
	
	
    def spew_package_list(self):
	pass
	
    
    def announce_new_package(self):
	pass 
	
    def invalidate_package_torrent(self, torrent):
	pass 
	
	
	
	
	
    



class Json_Protocol(Protocol):
    
    def dataReceived(self, data):
	#self.transport.write(data)
	try:
	    print json.loads(data)
	except:
	    print "Could not parse json data"
	
	
    def connectionMade(self):
	self.transport.write("json-server 1.0 for tpm")
	

def main():
    f = Factory()
    f.protocol = Json_Protocol #<-- This inits Json_Protocol everytime something is recieved. 
    reactor.listenTCP(8000, f)
    print "Running"
    reactor.run()


if __name__ == '__main__':
    main()
