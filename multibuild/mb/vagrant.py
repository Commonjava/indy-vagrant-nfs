import os
import requests
import time
import mb.util

def wait_for_indy(indy_url):
    max_tries=30
    ready = False
    for t in range(max_tries):
        print "Attempting to contact Indy..."
        try:
            resp = requests.head(indy_url, timeout=1)
            if resp.status_code == 200:
                ready = True
                break
            else:
                print "...Indy isn't ready yet."
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            print "...Indy isn't ready yet."
            # nop

        print "Sleeping 10s before next attempt"
        time.sleep(10)

    if not ready:
        raise Exception("Indy isn't responding on: %s. Aborting test run." % indy_url)

def run_vagrant_commands(section, indy_url):
    cmd_sections = section.get('run')
    if cmd_sections is not None:
        for cmd_section in cmd_sections:
            host = cmd_section['host']
            for cmd in cmd_section['commands']:
                mb.util.run_cmd("vagrant ssh -c '%s' %s" % (cmd, host), fail=True)
            if cmd_section.get('wait-for-indy') is True:
                wait_for_indy(indy_url)

def run_vagrant_copy_ops(section, project_dir):
    copy_ops = section.get('copy')
    if copy_ops is not None:
        mb.util.run_cmd("vagrant ssh-config > .vagrant/ssh-config", fail=True)

        for src in copy_ops:
            dest = copy_ops[src]
            mb.util.run_cmd(("scp -q -r -F .vagrant/ssh-config %s %s" % (src, dest)).format(project_dir=project_dir), fail=True)

def vagrant_env(build_config, env, indy_url, vagrant_dir, project_dir):
    vagrant = build_config.get('vagrant')
    if vagrant is not None:
        cwd = os.getcwd()
        try:
            if vagrant_dir is not None:
                print "Switching to vagrant directory: %s" % vagrant_dir
                os.chdir(vagrant_dir)

            section = vagrant.get(env)
            if section is not None:
                run_vagrant_copy_ops(section, project_dir)
                run_vagrant_commands(section, indy_url)
        finally:
            os.chdir(cwd)

