import os
import sys
from datetime import datetime as dt

def run_cmd(cmd, fail=True):
    """Run the specified command. If fail == True, and a non-zero exit value 
       is returned from the process, then exit the program
    """
    print cmd
    ret = os.system(cmd)
    if ret != 0:
        print 'Error running command'
        if fail:
            sys.exit(1)


def setup_builddir(projectdir, idx):
    if os.path.isdir('builds') is False:
        os.makedirs('builds')

    builddir="builds/project-%s-%s" % ((dt.now()-dt.utcfromtimestamp(0)).total_seconds(), idx)

    run_cmd("git clone file://%s %s" % (projectdir, builddir))
    
    return os.path.join(os.getcwd(), builddir)
