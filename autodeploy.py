#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import BaseHTTPServer

import config


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
        payload = self.parseRequest()
        git = payload['repository']['url']
        repo = self.matchPath(git)
        self.deploy(repo)

    def do_GET(self):
        self.respond(200)
        self.wfile.write('Waiting for git web hook callback......')

    def deploy(self, repo):
        try:
            subprocess.call(['cd "%s"' % repo['path']], shell=True)
            self.log_message('cd to %s', repo['path'])
            subprocess.call(['git pull origin master'], shell=True)
            self.log_message('git pull origin master')
            if repo['github']:
                subprocess.call(['git push github master'], shell=True)
                self.log_error('git push github master')

        except:
            self.log_error("Update Fail!")

    def respond(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def parseRequest(self):
        length = int(self.headers.getheader('content-length'))
        body = self.rfile.read(length)
        return json.loads(body)

    def matchPath(self, git):
        for repo in config.repos:
            if git == repo['git']:
                return repo

        return None


def main():
    port = 34567
    print "AutoDeploy Service start on %s " % port
    server = BaseHTTPServer.HTTPServer(('127.0.0.1', port), AutoDeployHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
