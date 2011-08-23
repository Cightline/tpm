import os


def check(path):
	if os.path.exists(os.path.expanduser(path)):
	    return True
	else:
	    print "You do not have a config file"
	    return False
