#!/usr/bin/env python

import os
import sys
import argparse
import mb
import mb.reporter
import requests
import json
from Queue import Queue

parser = argparse.ArgumentParser()

parser.add_argument('indy_url', help='Indy base url (eg. http://localhost:8080)')
parser.add_argument('-t', '--threads', type=int, default=4, help='Number of report verifiers')

args = parser.parse_args()

report_queue = Queue()

try:
    task_ids = mb.reporter.get_sealed_reports(args.indy_url)
    print "\n".join(task_ids)

    if not os.path.isdir('builds'):
        os.makedirs('builds')

    for t in range(args.threads):
        thread = mb.reporter.Reporter(report_queue)
        thread.daemon = True
        thread.start()

    for tid in task_ids:
        builddir = "builds/%s" % tid
        if not os.path.isdir(builddir):
            os.makedirs(builddir)

        report_queue.put((builddir, args.indy_url, tid))
        # mb.reporter.verify_report(builddir, args.indy_url, tid)

    report_queue.join()
except (KeyboardInterrupt, SystemExit) as e:
    print e
    print "Quitting."

