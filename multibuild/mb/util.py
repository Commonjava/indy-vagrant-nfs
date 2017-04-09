import os
import sys
from datetime import datetime as dt

def run_cmd(cmd, fail=True):
    """Run the specified command. If fail == True, and a non-zero exit value 
       is returned from the process, raise an exception
    """
    print cmd
    ret = os.system(cmd)
    if ret != 0:
        print "Error running command: %s (return value: %s)" % (cmd, ret)
        if fail:
            raise Exception("Failed to run: '%s' (return value: %s)" % (cmd, ret))


def setup_builddir(projectdir, idx):
    if os.path.isdir('builds') is False:
        os.makedirs('builds')

    builddir="builds/project-%s-%s" % ((dt.now()-dt.utcfromtimestamp(0)).total_seconds(), idx)

    run_cmd("git clone file://%s %s" % (projectdir, builddir))
    
    return os.path.join(os.getcwd(), builddir)
