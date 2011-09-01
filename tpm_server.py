import os, json, ConfigParser, server_sql as sql, optparse, Pyro.core, check_config, gnupg


class Server(Pyro.core.ObjBase):
    def __init__(self):
<<<<<<< HEAD
        
        Pyro.core.ObjBase.__init__(self)
        

        #Load up the server conifg.
        cfg = ConfigParser.RawConfigParser()
        self.config = "/etc/tpm_server/config"
        check_config.init_server()
=======
	#Init Pyro
	Pyro.core.ObjBase.__init__(self)
	
	#Load up the server conifg.
	check_config.init_server()
        cfg = ConfigParser.RawConfigParser()
        self.config = "/etc/tpm_server/config"
>>>>>>> no_indent
        if check_config.check(self.config):
            cfg.readfp(open(self.config))
            self.package_file = cfg.get("package", "dir")
            self.sql = sql.Database(self.package_file)
            self.random_package_num = 100000
	    self.init_gnupg()
            self.parse_options()
        
    def return_type(self):
	return "tpm_server"

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
            
<<<<<<< HEAD
            
    
    def add_dummy_packages(self, num):
        total = 0
        print "Adding %s dummy packages..." % self.options.add_dummy
        import random
        for x in range(int(self.options.add_dummy)):
            num = random.randrange(0, self.random_package_num)
            if self.sql.add_package("dummy_package%s" % (num), num, num):
                total += 1
            
        print "Done, added %s dummy packages" % total

=======
    
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
    
    def add_package(self, path):
	package_base = os.path.basename(path)
	package_name = package_base.split("-")[0]
	package_version = package_base.split(package_base.split("-")[-1].split(".pkg.tar.xz")[0])[0].split(package_name)[1].split()
	print "Adding package: name: %s version: %s" % (package_name, package_version)
	#if self.sql.add_package(package_name, 
    
    def d(self, torrent_name):
	if torrent_name in self.sql.return_packages(): 
	    return True
	else:
	    return False
>>>>>>> no_indent
    
    def invalidate_package_torrent(self, torrent):
        pass 

    
    
    #This is for when a client creates (automatically) a new package torrent that does not already exist.
    def announce_new_package(self, package_name):
        print "New torrent package %s" % package_name
    

<<<<<<< HEAD
if os.getuid() != 0:
            print "Run me as root"
            exit()
=======
check_config.check_root()
>>>>>>> no_indent

Pyro.core.initServer()
daemon=Pyro.core.Daemon()
uri = daemon.connect(Server(), "tpm_server")
print "Port: %s URI: %s" % (daemon.port, uri)
daemon.requestLoop()

