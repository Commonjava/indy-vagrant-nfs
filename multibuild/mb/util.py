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


def setup_builddir(builds_dir, projectdir, tid_base, idx):
    if os.path.isdir(builds_dir) is False:
        os.makedirs(builds_dir)

    builddir="%s/%s-%s-%s" % (builds_dir, tid_base, dt.now().strftime("%Y%m%dT%H%M%S"), idx)

    run_cmd("git clone file://%s %s" % (projectdir, builddir))
    
    return os.path.join(os.getcwd(), builddir)
