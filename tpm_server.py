import os, json, ConfigParser, server_sql as sql, optparse, Pyro.core, check_config


class Server(Pyro.core.ObjBase):
    def __init__(self):
        
        Pyro.core.ObjBase.__init__(self)
        

        #Load up the server conifg.
        cfg = ConfigParser.RawConfigParser()
        self.config = "/etc/tpm_server/config"
        check_config.init_server()
        if check_config.check(self.config):
            cfg.readfp(open(self.config))
            self.package_file = cfg.get("package", "dir")
            self.sql = sql.Database(self.package_file)
            self.random_package_num = 100000
            self.parse_options()
            self.package_list = self.sql.return_packages()
        

    def parse_options(self):
        parser = optparse.OptionParser()
        
        parser.add_option('-d', '--dummy-package',
                          action="store",
                          dest='add_dummy', 
                          help="Add [num] of dummy packages (used for stress testing)", 
                          )
        
        (self.options, self.args) = parser.parse_args()
        
        if self.options.add_dummy:
            self.add_dummy_packages(self.options.add_dummy)
            
            
    
    def add_dummy_packages(self, num):
        total = 0
        print "Adding %s dummy packages..." % self.options.add_dummy
        import random
        for x in range(int(self.options.add_dummy)):
            num = random.randrange(0, self.random_package_num)
            if self.sql.add_package("dummy_package%s" % (num), num, num):
                total += 1
            
        print "Done, added %s dummy packages" % total

    
    def invalidate_package_torrent(self, torrent):
        pass 

    
    
    #This is for when a client creates (automatically) a new package torrent that does not already exist.
    def announce_new_package(self):
        pass 
    

if os.getuid() != 0:
            print "Run me as root"
            exit()

Pyro.core.initServer()
daemon=Pyro.core.Daemon()
uri = daemon.connect(Server(), "tpm_server")
print "Port: %s URI: %s" % (daemon.port, uri)
daemon.requestLoop()

