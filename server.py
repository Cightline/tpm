import os, json, ConfigParser, sqldatabase, optparse, check_config
from twisted.internet import reactor, interfaces 
from twisted.spread import pb, jelly
from twisted.spread.util import FilePager



class Json_Server(pb.Root):
    def __init__(self):
        #Load up the server conifg.
        cfg = ConfigParser.RawConfigParser()
        self.config_file = os.path.expanduser("~/.tpm_server/config")
        if check_config.check(self.config_file):
            cfg.readfp(open(self.config))
            self.package_file = cfg.get("package", "dir")
            self.sql = sqldatabase.Database(self.package_file)
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
            
            
    
        #This function will tell the tracker that the package/torrent is invalid. 
    
    def add_dummy_packages(self, num):
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
    
    def invalidate_package_torrent(self, torrent):
        pass 
    
    
    
    
    #This remote function returns the package list to the client.
    def remote_spew_package_list(self, *args): #This is gonna be poorly written until I figure something out
        if args[0]:
            req_size = args[0]
            
        print "[Server] Spewing package list to client..."
        total = len(self.package_list)
        chunk = req_size
        print "Chunk: %s, total: %s " % (chunk, total)
        
        return self.package_list[chunk[0]:chunk[1]], len(self.package_list)
    
    
    #This is for when a client creates (automatically) a new package torrent that does not already exist.
    def remote_announce_new_package(self):
        pass 
    





if __name__ == "__main__":
    reactor.listenTCP(8000, pb.PBServerFactory(Json_Server()))
    reactor.run()
