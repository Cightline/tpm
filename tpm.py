#!/usr/bin/env python2
import cPickle, os, ConfigParser, json, optparse, cStringIO,check_config, sys
from twisted.internet import reactor, defer, protocol
from twisted.python import util    


#This is the "mask" to tpmd. It communicates with the daemon. This is needed because the daemon is a torrent seeder/leacher. 
#It simply tells the daemon what it needs and kindly waits for a reply. 


class tpm():
    def __init__(self):
	
	self.config = "/etc/tpm/config"
	
	#Check to see if our config exists, then grab some args.
	if check_config.check(self.config):
	    cfg = ConfigParser.RawConfigParser()
	    cfg.readfp(open(self.config))
	    self.json_server = cfg.get("server", "address")
	    self.json_port = cfg.get("server", "port")
	    self.daemon_port = open("/etc/tpm/d_port",'r').read()
	
	    
	#Setup our command line options
	parser = optparse.OptionParser()
	
	
	parser.add_option('--update',
				action="store_true",
				dest='update_package_list', 
				help="Update your local package list", 
			)
			
	parser.add_option('-s', '--search',
				action="store",
				dest="search_package",
				help="Search for a package",
			)
			
	parser.add_option('-l', '--list',
				action="store_true",
				dest="list_packages",
				help="List packages"
			)
	
	parser.add_option('--upload',
				action="store",
				dest="upload_package",
				help="tpm -u [package], used to manually upload a package torrent for testing"
				
			)
			
	parser.add_option('-p', '--package-manager',
				action="store",
				dest="package_manager",
				help="package manager hook"
			)
			
	(self.options, self.args) = parser.parse_args()
	
    
    def message(self, message):
	self.instance.transport.write(message)
    
    def check_done(self):
	if reactor.running:
	    #It seems to throw a error, regardless of what you do, I'm thinking its something to do with the async properties it has. 
	    try:
		reactor.stop()
	    except:
		pass
	else:
	    exit()
	
    def list_torrents(self, torrent=None, callback=False):
	
	if callback:
	    if torrent:
		print torrent
	    else:
		print "No torrents found"
		
	else:
	    self.message(json.dumps({"list":None}))
	
	
    def search_torrent(self, search, searching=True):
	if searching:
	    self.message(json.dumps({"search":search}))
	else:
	    if search:
		print search
		self.check_done()
	    else:
		print "Package not found"
		self.check_done()
	
    
    def handle_instance(self, instance):
	self.instance = instance
	self.handle_args()
    
    def delegate_data(self, data):
	data = json.loads(data)
	
	if "search" in data.keys():
	    self.search_torrent(data["search"], False)
	if "list" in data.keys():
	    self.list_torrents(data["list"], True)
    
    def handle_args(self):
	
	if self.options.update_package_list:
	    self.d_update_package_list()
	    
	elif self.options.search_package:
	    self.search_torrent(self.options.search_package.lower())
	    
	elif self.options.list_packages:
	    self.list_torrents()
	    
	elif self.options.upload_package:
	    self.instance.transport.write(json.dumps({"upload_package":self.options.upload_package}))
	
	elif self.options.package_manager:
	    pass
	    
	else:
	    exit() #implement the help arg here


class tpm_Proto(protocol.Protocol):
    
    def connectionMade(self):
	#print "Connected to daemon"
	t.handle_instance(self)
    
    def dataReceived(self, data):
	t.delegate_data(data)

if __name__ == "__main__":
    check_config.check_root()
    check_config.init_tpm()
    t = tpm()
    factory = protocol.ClientFactory()
    factory.protocol = tpm_Proto
    reactor.connectTCP("localhost", 8001, factory)
    reactor.run()
    


    
