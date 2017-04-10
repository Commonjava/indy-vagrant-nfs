import click
import os
import yaml
import mb.util
import mb.vagrant
import mb.builder
import mb.reporter
from Queue import Queue
import time
from datetime import datetime as dt
import requests

@click.command()
@click.argument('testfile', type=click.Path(exists=True))
@click.argument('indy_url')
@click.option('--delay', '-D', help='Delay between starting builds')
@click.option('--vagrant-dir', '-V', help='The Vagrant environment directory', type=click.Path(exists=True))
def build(testfile, indy_url, delay, vagrant_dir):
    with open(testfile) as f:
        build_config = yaml.safe_load(f)

    vagrant_dir = mb.vagrant.find_vagrant_dir(vagrant_dir)

    if delay is None:
        delay = 0
    else:
        delay = int(delay)

    cwd = os.getcwd()
    try:
        project_dir = os.path.abspath(os.path.dirname(testfile))
        builds_dir = "builds-%s" % dt.now().strftime("%Y%m%dT%H%M%S")

        tid_base = os.path.basename(project_dir)

        mb.vagrant.init_ssh_config(vagrant_dir)
        mb.vagrant.vagrant_env(build_config, 'pre-build', indy_url, vagrant_dir, project_dir, os.path.join(project_dir, builds_dir))

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
                builddir = mb.util.setup_builddir(builds_dir, project_src_dir, tid_base, x)
                build_queue.put((builddir, indy_url, build_config['proxy-port'], (x % int(build['threads']))*int(delay)))

            build_queue.join()

            mb.vagrant.vagrant_env(build_config, 'post-build', indy_url, vagrant_dir, project_dir, builds_dir)
            mb.vagrant.vagrant_env(build_config, 'pre-report', indy_url, vagrant_dir, project_dir, builds_dir)

            for t in range(int(report['threads'])):
                thread = mb.reporter.Reporter(report_queue)
                thread.daemon = True
                thread.start()

            report_queue.join()
        except Exception as e:
            print e
            print "Quitting."

        mb.vagrant.vagrant_env(build_config, 'post-report', indy_url, vagrant_dir, project_dir, builds_dir)
    finally:
        os.chdir(cwd)

@click.command()
@click.argument('testfile', type=click.Path(exists=True))
@click.argument('indy_url')
@click.option('--vagrant-dir', '-V', help='The Vagrant environment directory', type=click.Path(exists=True))
def check(testfile, indy_url, vagrant_dir=None):
    with open(testfile) as f:
        build_config = yaml.safe_load(f)

    vagrant_dir = mb.vagrant.find_vagrant_dir(vagrant_dir)

    cwd = os.getcwd()
    try:
        project_dir = os.path.abspath(os.path.dirname(testfile))
        reports_dir = os.path.join(project_dir, 'reports')
        if not os.path.isdir(reports_dir):
            os.makedirs(reports_dir)

        mb.vagrant.init_ssh_config(vagrant_dir)
        mb.vagrant.vagrant_env(build_config, 'pre-report', indy_url, vagrant_dir, project_dir, reports_dir)

        os.chdir(project_dir)

        report = build_config['report']

        report_queue = Queue()

        try:
            task_ids = mb.reporter.get_sealed_reports(indy_url)
            print "\n".join(task_ids)

            for t in range(int(report['threads'])):
                thread = mb.reporter.Reporter(report_queue)
                thread.daemon = True
                thread.start()

            for tid in task_ids:
                builddir = os.path.join(reports_dir, tid)
                if not os.path.isdir(builddir):
                    os.makedirs(builddir)

                report_queue.put((builddir, indy_url, tid))
                # mb.reporter.verify_report(builddir, args.indy_url, tid)

            report_queue.join()
        except (KeyboardInterrupt, SystemExit) as e:
            print e
            print "Quitting."

        mb.vagrant.vagrant_env(build_config, 'post-report', indy_url, vagrant_dir, project_dir, reports_dir)
    finally:
        os.chdir(cwd)

