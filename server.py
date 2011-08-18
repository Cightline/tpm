
import os, json, ConfigParser, sqldatabase
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory


class Json_Server():
    def __init__(self):
	cfg = ConfigParser.RawConfigParser()
	cfg.readfp(open(os.path.expanduser("~/.tpm_server/config")))
	
	self.package_file = cfg.get("package", "dir")
	if os.path.exists(self.package_file):
	    sql = sqldatabase.Database(self.package_file)
	    
	else:
	    print "I did not load the package file"
	    
	    
	    
    def delegate(self, json_data):
	
	#print "Json data",  json_data
	#print "Type" , type(json_data)
	#There is only going to be a few functions that need to be passed on, so I will use if statements.
	
	if json_data == "new_package":
	    print "Verifing integrity of new package"
	    self.announce_new_package(json_data)
	
	elif json_data == ["request_package_list"]:
	    print "Sending package list to client"
	    self.spew_package_list(json_data)
	    
	#Thats all the functions I can think of for now
	
    def spew_package_list(self, json_data):
	pass
	
    
    def announce_new_package(self):
	pass 
	
    def invalidate_package_torrent(self, torrent):
	pass 
	
	
	
	
	
    



class Json_Protocol(Protocol):
    
    def dataReceived(self, data):
	try:
	    json_data = json.loads(data)
	except:
	    print "Could not parse json data"
	
	J.delegate(json_data)
	
	
    def connectionMade(self):
	self.transport.write(json.dumps({"json-server":"1.0"}))
	


    
if __name__ == '__main__':
    J = Json_Server()
    F = Factory()
    F.protocol = Json_Protocol #<-- This inits Json_Protocol everytime something is recieved. 
    reactor.listenTCP(8000, F)
    print "Running"
    reactor.run()
