#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import datetime
import subprocess
import BaseHTTPServer

SETTINGS_FILE = "settings.json"

class AutoDeployHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """ AutoDeploy类 """

    def do_POST(self):
        event = self.headers.getheader('X-Gitlab-Event')
        if event != 'Push Hook':
            self.respond(304)
            self.wfile.write('Only Support Push Hook')
            return

        self.respond(200)
        self.wfile.write('Push Hook Success!')
        self.log("Web Hook Callback.")
        payload = self.parseRequest()
        git = payload['repository']['url']
        self.log("Receive " + git)
        path = self.matchPath(git)
        self.log("Updating " + path)
        self.deploy(path)

    def do_GET(self):
        self.respond(200)
        self.wfile.write('Waiting for git web hook callback......')
        self.log(self.path)

    def loadConfig(self):
        try:
            settings = open(SETTINGS_FILE).read()
        except:
            sys.exit("Load settings file fail!")

        try:
            self.config = json.loads(settings)
        except:
            sys.exit("Load settings data fail!")

    def log(self, msg):
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + msg

    def deploy(self, path):
        try:
            subprocess.call(['cd "' + path + '" && git pull'], shell=True)
        except:
            self.log("Update Fail!")

    def respond(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def parseRequest(self):
        length = int(self.headers.getheader('content-length'))
        body = self.rfile.read(length)
        return json.loads(body)

    def matchPath(self, git):
        path = None
        repos = self.loadConfig()
        for repo in repos:
            if git == repo['git']:
                path = repo['path']
                break

        return path


def main():
    port = 34567
    print "AutoDeploy Service started on %s" % port
    server = BaseHTTPServer.HTTPServer(('', port), AutoDeployHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
