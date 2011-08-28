import os


def check(path):
	if os.path.exists(os.path.expanduser(path)):
	    return True
	else:
	    return False 
	    
	    
def init_tpm():
    if os.path.exists("/etc/tpm/config"):
	return True
    else:
	try:
	    fp = open("/etc/tpm/config","w")
	except:
	    print "[config_check] I cannot open /etc/tpm/config, for writting"
	    exit()
	    
	import ConfigParser
	print "[check_config] Creating default tpm config..."
	cfg = ConfigParser.RawConfigParser()
	sections = ["tracker", "server"]
	for s in sections:
	    cfg.add_section(s)
	    
	cfg.set("tracker", "port", "6881 6891")
	cfg.set("tracker", "address", "udp://localhost:6969")
	cfg.set("server", "port", "8000")
	cfg.set("server", "address", "localhost")
	cfg.write(fp)
	fp.close()
	print "[check_config] Done, re-run me"
	exit()


def create_server_config():
    try:
	fp = open("/etc/tpm_server/config", "w")
    except:
	print "[config_check] I cannot open /etc/tpm/config, for writting"
	exit()
		
    import ConfigParser 
    print "[check_config] Creating default server config..."
    cfg = ConfigParser.RawConfigParser()
    sections = ["package"]
    for s in sections:
	cfg.add_section(s)
    cfg.set("package", "dir", "/etc/tpm_server/package.db")
    cfg.write(fp)
    fp.close()
    print "[check_config] Done, re-run me"
    exit()

def init_server():
    if os.path.exists("/etc/tpm_server"):
	if os.path.exists("/etc/tpm_server/config"):
	    return True
	else:
	    create_server_config()
    else:
	os.mkdir("/etc/tpm_server")
	create_server_config()
