import click
import os
import yaml
import mb.util
import mb.vagrant
import mb.builder
import mb.reporter
from Queue import Queue
import time
import requests

DELAY=0

@click.command()
@click.argument('testfile', type=click.Path(exists=True))
@click.argument('indy_url')
@click.option('--vagrant-dir', '-V', help='The Vagrant environment directory', type=click.Path(exists=True))
def build(testfile, indy_url, vagrant_dir):
    with open(testfile) as f:
        build_config = yaml.safe_load(f)

    if vagrant_dir is not None:
        vagrant_dir = os.path.abspath(vagrant_dir)

    cwd = os.getcwd()
    try:
        project_dir = os.path.abspath(os.path.dirname(testfile))

        mb.vagrant.vagrant_env(build_config, 'pre-build', indy_url, vagrant_dir, project_dir)

        os.chdir(project_dir)

        build = build_config['build']
        report = build_config['report']

        project_src_dir = build.get('project-dir') or 'project'
        project_src_dir = os.path.join(os.getcwd(), project_src_dir)

        build_queue = Queue()
        report_queue = Queue()

        try:
            for t in range(int(build['threads'])):
                thread = mb.builder.Builder(build_queue, report_queue)
                thread.daemon = True
                thread.start()

            for x in range(build['builds']):
                builddir = mb.util.setup_builddir(project_src_dir, x)
                build_queue.put((builddir, indy_url, build_config['proxy-port'], (x % int(build['threads']))*DELAY))

            build_queue.join()

            for t in range(int(report['threads'])):
                thread = mb.reporter.Reporter(report_queue)
                thread.daemon = True
                thread.start()

            report_queue.join()
        except Exception as e:
            print e
            print "Quitting."

        mb.vagrant.vagrant_env(build_config, 'post-build', indy_url, vagrant_dir, project_dir)
    finally:
        os.chdir(cwd)

@click.command()
@click.argument('testfile', type=click.Path(exists=True))
@click.argument('indy_url')
@click.option('--vagrant-dir', '-V', help='The Vagrant environment directory', type=click.Path(exists=True))
def check(testfile, indy_url, vagrant_dir=None):
    with open(testfile) as f:
        build_config = yaml.safe_load(f)

    if vagrant_dir is not None:
        vagrant_dir = os.path.abspath(vagrant_dir)

    cwd = os.getcwd()
    try:
        project_dir = os.path.abspath(os.path.dirname(testfile))

        mb.vagrant.vagrant_env(build_config, 'pre-report', indy_url, vagrant_dir, project_dir)

        os.chdir(project_dir)

        report = build_config['report']

        report_queue = Queue()

        try:
            task_ids = mb.reporter.get_sealed_reports(indy_url)
            print "\n".join(task_ids)

            if not os.path.isdir('builds'):
                os.makedirs('builds')

            for t in range(int(report['threads'])):
                thread = mb.reporter.Reporter(report_queue)
                thread.daemon = True
                thread.start()

            for tid in task_ids:
                builddir = "builds/%s" % tid
                if not os.path.isdir(builddir):
                    os.makedirs(builddir)

                report_queue.put((builddir, indy_url, tid))
                # mb.reporter.verify_report(builddir, args.indy_url, tid)

            report_queue.join()
        except (KeyboardInterrupt, SystemExit) as e:
            print e
            print "Quitting."

        mb.vagrant.vagrant_env(build_config, 'post-report', indy_url, vagrant_dir, project_dir)
    finally:
        os.chdir(cwd)

