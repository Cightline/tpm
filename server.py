import os, json, ConfigParser, sqldatabase, optparse
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
	self.random_package_num = 100000
	self.parse_options()
	
	
    def parse_options(self):
	parser = optparse.OptionParser()
	
	parser.add_option('-d', '--dummy-package',
				action="store",
				dest='add_dummy', 
				help="Add [num] of dummy packages (used for stress testing)", 
			)
	
	(self.options, self.args) = parser.parse_args()
	
	if self.options.add_dummy:
	    print "Adding %s dummy packages..." % self.options.add_dummy
	    import random
	    for x in range(int(self.options.add_dummy)+1):
		num = random.randrange(0, self.random_package_num)
		try:
		    self.sql.add_package("dummy_package%s" % (num), num, num)
		    print "[dummypackage%s]: added" % (num)
		except:
		    print "[dummypackage%s]: NOT added" % (num)
	    print "Done, added %s dummy packages" % x
	    
    
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
