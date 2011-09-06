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
	
	self.SUCCESS = {"update_database":"Database updated"}
	self.ERROR = {"update_database":"Could not update database"}
	
	self.q = []
	
	
	#Setup our command line options
	parser = optparse.OptionParser()
	
	
	parser.add_option('--update',
				action="store_true",
				dest='update_database', 
				help="Update your local torrent list", 
			)
			
	parser.add_option('-s', '--search',
				action="store",
				dest="search_torrent",
				help="Search for a package",
			)
			
	parser.add_option('-l', '--list',
				action="store_true",
				dest="list_torrents",
				help="List packages"
			)

			
	parser.add_option('--torrent-largest',
				action="store",
				dest="torrent_largest",
				help="--spider [path] find the biggest file and torrent it)"
			)
			
			
	(self.options, self.args) = parser.parse_args()
	
    
    def message(self, message):
	self.instance.transport.write(json.dumps(message))
    
    def check_done(self):
	
	if len(self.q) == 0:
	    try:
		reactor.stop()
	    except:
		exit()
	else:
	    return False
	
    def list_torrents(self, torrent=None, callback=False):
	
	if callback == False:
	    self.message({"list":None})
	
	elif callback and torrent:
	    for t in torrent:
		print t["name"]
	    self.remove_check("list_torrents")
	    
	else:
	    print "No torrents found"
	    self.remove_check("list_torrents")
	
	
    def search_torrent(self, search, searching=True):

	if searching:
	    self.message({"search":search})
	
	elif search == []:
	    print "Package not found"
	    self.remove_check("search_torrent")
	    
	elif search:
	    for t in search:
		print t
	    self.remove_check("search_torrent")
	    
	
    def update_database(self, value=None, callback=False):
	
	if callback:
	    
	    if value:
		print "Wrote %s packages" % value[1]
		self.remove_check("update_database")
	    else:
		print "Nothing updated"
		self.remove_check("update_database")
	else:
	    print "Updating..."
	    self.message({"update_database":None})
	
    
    
    def torrent_largest(self, data):
	if raw_input('Would you like to torrent "%s" [%s]: ' % (data[0], data[1])).startswith("y"):
	    self.message({"torrent_largest_c":True})
	
    
	else:
	    self.message({"torrent_largest_c":False})
    
    def remove_check(self, q):
	self.q.remove(q)
	self.check_done()

    
    def handle_instance(self, instance):
	self.instance = instance
	self.handle_args()

	
    def delegate_data(self, data):
	print "data", data 
	data = json.loads(data)
	
	if "search" in data.keys():
	    self.search_torrent(data["search"], False)
	    
	if "list" in data.keys():
	    self.list_torrents(data["list"], True)
	    
	if "update" in data.keys():
	    self.update_database(data["update"], True)
	    
	if "spider" in data.keys():
	    self.spider(data["spider"])
	    
	if "torrent_largest_q" in data.keys():
	    self.torrent_largest(data["torrent_largest_q"])
    
    def handle_args(self):
	
	if self.options.update_database:
	    self.q.append("update_database")
	    self.update_database()
	    
	elif self.options.search_torrent:
	    self.q.append("search_torrent")
	    self.search_torrent(self.options.search_torrent.lower(), True)
	    
	elif self.options.list_torrents:
	    self.q.append("list_torrents")
	    self.list_torrents()
	
	elif self.options.torrent_largest:
	    self.q.append("torrent_largest")
	    self.message({"torrent_largest":self.options.torrent_largest})
	    


class tpm_Proto(protocol.Protocol):
    
    def connectionMade(self):
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
    


    
