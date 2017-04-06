#!/usr/bin/env python

import os
import sys
import json
import requests
import shutil
import hashlib
from threading import Thread

EXTS = ['.jar', '.pom', '.tar.gz', '.zip']

class Reporter(Thread):
    def __init__(self, report_queue):
        Thread.__init__(self)
        self.queue = report_queue

    def run(self):
        while True:
            try:
                (builddir, report) = self.queue.get()

                report_name = os.path.basename(builddir)

                input_name = os.path.join(builddir, "%s-report.json" % report_name)
                with open(input_name, 'w') as f:
                    f.write(json.dumps(report, indent=2))

                downloads = report.get('downloads') or []
                uploads = report.get('uploads') or []

                tmp = 'content-temp'
                if os.path.isdir(tmp):
                    shutil.rmtree(tmp)

                os.makedirs(tmp)

                print "Got %d downloads and %d uploads" % (len(downloads), len(uploads))

                entries = []
                if uploads is not None:
                    for e in uploads:
                        entries.append({'dataset': 'upload', 'entry': e})

                if downloads is not None:
                    for e in downloads:
                        entries.append({'dataset': 'download', 'entry': e})

                result = {'results': []}
                self._process_partition(entries, result['results'])

                output_name = os.path.join(builddir, "%s-verify.json" % report_name)
                with open(output_name, 'w') as f:
                    f.write(json.dumps(result, indent=2))

                print "Wrote: %s (%d results)" % (output_name, len(result['results']))
            except KeyboardInterrupt:
                print "Keyboard interrupt in process: ", process_number
                break
            finally:
                self.queue.task_done()

    def _process_partition(self, partition, results):
        for p in partition:
            entry = p['entry']
            path = entry['path'][1:]
            proceed = False
            for e in EXTS:
                if path.endswith(e):
                    proceed = True
                    break

            if proceed:
                url = entry['localUrl']
                print "Checking: %s" % url

                r = requests.get(url, stream=True)
                if r.status_code != 200:
                    raise Exception("Failed to download: %s" % url)

                header_size=int(r.headers['content-length'])

                dest = os.path.join(tmp, path)
                destdir = os.path.dirname(dest)
                if not os.path.isdir(destdir):
                    os.makedirs(destdir)

                with open(dest, 'wb') as f:
                    #r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)

                entry_data = {'path': path, 'local_url': url, 'type':p['dataset']}

                dest_sz = os.path.getsize(dest)
                if entry['size'] != dest_sz or entry['size'] != header_size or dest_sz != header_size:
                    entry_data['size'] = {'success': False, 'record': entry['size'], 'header': header_size, 'calculated': dest_sz}
                else:
                    entry_data['size'] = {'success': True}

                self._compare_checksum('md5', url, dest, entry, entry_data)
                self._compare_checksum('sha1', url, dest, entry, entry_data)
                # compare_checksum('sha256', url, dest, entry, entry_data)

                append=False
                for k in ['size', 'md5', 'sha1']:
                    if entry[k]['success'] is False:
                        append = True
                        break

                if append is True:
                    results.append(entry_data)

        return results

    def _compare_checksum(self, checksum_type, url, dest, entry, entry_data):
        check_url = url + '.' + checksum_type
        print "Retrieving checksum: %s" % check_url
        
        r = requests.get(check_url)
        if r.status_code == 200:
            check_file = r.text
        else:
            check_file = None

        check = hashlib.new(checksum_type, open(dest, 'rb').read()).hexdigest()
        if entry[checksum_type] != check: # or entry[checksum_type] != check_file or check != check_file:
            entry_data[checksum_type] = {'success': False, 'record': entry[checksum_type], 'file': check_file, 'calculated': check}
        else:
            entry_data[checksum_type] = {'success': True}

