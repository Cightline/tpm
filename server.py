
import os, json
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory

class Echo(Protocol):
    
    
    def __init__(self):
	cfg = ConfigParser.RawConfigParser()
	cfg.readfp(open(os.path.expanduser("~/.tpm_server/config")))
	self.package_file = cfg.get("package", "dir")
	if os.path.exists(self.package_file):
	    try:
		json.load(open(self.package_file))
		print "Loaded package file"
	    except:
		print "I could not load the package file, exiting"
		exit(1)
	else:
	    if raw_input("I could not find the package file, should I create a empty one?").lower() == "y" or "yes":
		json.dump(["empty"], self.package_file)
		
	    
    
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
    f.protocol = Echo
    reactor.listenTCP(8000, f)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
