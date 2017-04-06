#!/usr/bin/env python

import os
from Queue import Queue
import argparse
import time

import mb
import mb.builder
import mb.reporter

DELAY=0

parser = argparse.ArgumentParser()

parser.add_argument('indy_url', help='Indy base url (eg. http://localhost:8080)')
parser.add_argument('-p', '--project', default='project', help='Directory to clone to serve as build root')
parser.add_argument('-b', '--total-builds', type=int, default=4, help='Number of total builds to run')
parser.add_argument('-t', '--threads', type=int, default=2, help='Number of builders')
parser.add_argument('-P', '--proxy-port', type=int, default=8081, help='Port for generic HTTP proxy')

args = parser.parse_args()

projectdir = os.path.join(os.getcwd(), args.project)

build_queue = Queue()
report_queue = Queue()

try:
    for t in range(args.threads):
        thread = mb.builder.Builder(build_queue, report_queue)
        thread.daemon = True
        thread.start()

    for x in range(args.total_builds):
        builddir = mb.setup_builddir(projectdir, x)
        build_queue.put((builddir, args.indy_url, args.proxy_port, (x % args.threads)*DELAY))

    build_queue.join()

    for t in range(args.threads):
        thread = mb.reporter.Reporter(report_queue)
        thread.daemon = True
        thread.start()

    report_queue.join()
except (KeyboardInterrupt, SystemExit):
    print "Quitting."

