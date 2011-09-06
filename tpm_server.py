import os, json, ConfigParser, server_sql as sql, optparse, check_config, gnupg

from twisted.internet import reactor, protocol

#TODO
#Add logger

#You need to create a symlink to the package database that points to [youserver.com]/tpm_server/torrent.db, if you want the clients to be able to update.


class Server():
    def __init__(self):
	
	#Load up the server conifg.
	check_config.init_server()
	cfg = ConfigParser.RawConfigParser()
	self.config = "/etc/tpm_server/config"
	
	if check_config.check(self.config):
	    cfg.readfp(open(self.config))
	    self.package_file = cfg.get("package", "dir")
	    self.sql = sql.Database(self.package_file)
	    self.random_package_num = 100000
	    self.init_gnupg()
	    self.parse_options()
	

    def parse_options(self):
	parser = optparse.OptionParser()
	
	parser.add_option('-d', '--dummy-package',
			  action="store",
			  dest='add_dummy', 
			  help="Add [num] of dummy packages (used for stress testing)", 
			  )
	
	parser.add_option('--add-package',
			  action="store",
			  dest="package_path",
			  help="Manually add a package"
			  )
	
	(self.options, self.args) = parser.parse_args()
	
	if self.options.add_dummy:
	    self.add_dummy_packages(self.options.add_dummy)
	
	elif self.options.package_path:
	    self.add_package(self.options.package_path)
	    
    
    def init_gnupg(self):
	gpg = gnupg.GPG(gnupghome=os.path.expanduser("~/"))
	print "[Gnupg] Initilized"
    
    def add_dummy_packages(self, num):
	total = 0
	print "Adding %s dummy packages..." % self.options.add_dummy
	import random
	for x in range(int(self.options.add_dummy)):
	    num = random.randrange(0, self.random_package_num)
	    if self.sql.add_package("dummy_package%s" % (num), num, num, num):
		total += 1
	    
	print "Done, added %s dummy packages" % total
    
    def add_package(self, name, version, location, sig):
	if self.sql.add_package(name, version, location, sig):
	    return True
	
	
    def does_torrent_exist(self, torrent_name):
	if torrent_name in self.sql.return_packages(): 
	    return True
    
    def invalidate_package_torrent(self, torrent):
	pass 


    def announce_new_package(self, package_name):
	print "New torrent package %s" % package_name
    

    def delegate_data(self, data, instance):
	print "data", data
	
	
	




class Server_Proto(protocol.Protocol):
    
    def connectionMade(self):
	print "Client connected"
	
    def dataReceived(self, data):
	print "recv_data", data 
	s.delegate_data(data, self)
	
    

if __name__ == "__main__":
    check_config.check_root()
    check_config.init_server()
    s = Server()
    factory = protocol.ServerFactory()
    factory.protocol = Server_Proto
    reactor.listenTCP(8000, factory)
    reactor.run()
	


