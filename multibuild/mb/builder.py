import os
import requests
import json
from threading import Thread
from urlparse import urlparse
import mb

SETTINGS = """
<?xml version="1.0"?>
<settings>
  <localRepository>%(dir)s/local-repo</localRepository>
  <mirrors>
    <mirror>
      <id>indy</id>
      <mirrorOf>*</mirrorOf>
      <url>%(url)s/api/folo/track/%(id)s/group/%(id)s</url>
    </mirror>
  </mirrors>
  <proxies>
    <proxy>
      <id>indy-httprox</id>
      <active>true</active>
      <protocol>http</protocol>
      <host>%(host)s</host>
      <port>%(proxy_port)s</port>
      <username>%(id)s+tracking</username>
      <password>foo</password>
      <nonProxyHosts>%(host)s</nonProxyHosts>
    </proxy>
  </proxies>
  <profiles>
    <profile>
      <id>resolve-settings</id>
      <repositories>
        <repository>
          <id>central</id>
          <url>%(url)s/api/folo/track/%(id)s/group/%(id)s</url>
          <releases>
            <enabled>true</enabled>
          </releases>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
        </repository>
      </repositories>
      <pluginRepositories>
        <pluginRepository>
          <id>central</id>
          <url>%(url)s/api/folo/track/%(id)s/group/%(id)s</url>
          <releases>
            <enabled>true</enabled>
          </releases>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
        </pluginRepository>
      </pluginRepositories>
    </profile>
    
    <profile>
      <id>deploy-settings</id>
      <properties>
        <altDeploymentRepository>%(id)s::default::%(url)s/api/folo/track/%(id)s/hosted/%(id)s</altDeploymentRepository>
      </properties>
    </profile>
    
  </profiles>
  <activeProfiles>
    <activeProfile>resolve-settings</activeProfile>
    
    <activeProfile>deploy-settings</activeProfile>
    
  </activeProfiles>
</settings>
"""

POST_HEADERS = {'content-type': 'application/json'}

class Builder(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            try:
                (builddir, indy_url, proxy_port) = self.queue.get()

                parsed = urlparse(indy_url)
                params = {'dir': builddir, 'url':indy_url, 'id': os.path.basename(builddir), 'host': parsed.hostname, 'port': parsed.port, 'proxy_port': proxy_port}

                self.setup(builddir, params);
                self.build(builddir)
                self.seal_folo_report(params)
                self.pull_folo_report(params)

                self.queue.task_done()
            except KeyboardInterrupt:
                print "Keyboard interrupt in process: ", process_number
                break

    def pull_folo_report(self, params):
        """Pull the Folo tracking report associated with the current build"""

        resp = requests.get("%(url)s/api/folo/admin/%(id)s/record" % params)
        resp.raise_for_status()

    def seal_folo_report(self, params):
        """Seal the Folo tracking report after the build completes"""

        resp = requests.post("%(url)s/api/folo/admin/%(id)s/record" % params, data={})
        resp.raise_for_status()

    def build(self, builddir):
        mb.run_cmd("mvn -f %(d)s/pom.xml -s %(d)s/settings.xml clean deploy" % {'d': builddir})

    def setup(self, builddir, params):
        """Create the hosted repo and group, then pull the Indy-generated Maven
           settings.xml file tuned to that group."""

        hosted = {
            'type': 'hosted', 
            'key': "hosted:%(id)s" % params, 
            'disabled': False, 
            'doctype': 'hosted', 
            'name': params['id'], 
            'allow_releases': True
        }

        print "POSTing: %s" % json.dumps(hosted, indent=2)

        resp = requests.post("%(url)s/api/admin/hosted" % params, json=hosted, headers=POST_HEADERS)
        resp.raise_for_status()

        group = {
            'type': 'group', 
            'key': "group:%(id)s" % params, 
            'disabled': False, 
            'doctype': 'group', 
            'name': params['id'], 
            'constituents': [
                "hosted:%(id)s" % params, 
                'group:public'
            ]
        }

        print "POSTing: %s" % json.dumps(group, indent=2)

        resp = requests.post("%(url)s/api/admin/group" % params, json=group, headers=POST_HEADERS)
        resp.raise_for_status()

        resp = requests.get("%(url)s/mavdav/settings/group/settings-%(id)s.xml" % params)
        resp.raise_for_status()

        with open("%s/settings.xml" % builddir, 'w') as f:
            f.write(SETTINGS % params)
