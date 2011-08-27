import os


def check(path):
	if os.path.exists(os.path.expanduser(path)):
	    return True
	else:
	    if os.path.exists("/etc/tpm"):
		print "You do not have a config file"
		return False
		    
	    else:
		if os.getuid() == 0:
		    os.mkdir("/etc/tpm")
		    return False
		else:
		    print "You do not have a /etc/tpm directory, re-run me as root and I will create it, otherwise run mkdir /etc/tpm"
		    return False
	    return False
