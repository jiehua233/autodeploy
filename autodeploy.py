#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import subprocess
import BaseHTTPServer
import sh


def get_logger():
    logger = logging.getLogger('autodeploy')
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    return logger


logger = get_logger()

class AutoDeployHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """ AutoDeploy类 """

    def do_GET(self):
        self.respond(200)
        self.wfile.write('Waiting for git web hook callback......')

    def do_POST(self):
        event = self.headers.getheader('X-Gitlab-Event')
        if event != 'Push Hook':
            self.respond(304)
            self.wfile.write('Only Support Push Hook')
            return

        self.respond(200)
        self.wfile.write('Push Hook Success!')

        git_url = self.parse_request()
        repository = self.match_repository(git_url)
        self.deploy(repository)

    def deploy(self, repository):
        logger.info("Processing %s", repository["git"])
        try:
            logger.info("Changing working directory to %s", repository["path"])
            sh.cd(repository["path"])
            sh.git("pull", "origin")

            result = git.fetch()
            self.log_error('cd "%s" && pull origin' % repo['path'])
            subprocess.call(['cd "%s" && git pull origin master' % repo['path']], shell=True)

            # sync to github
            if repository['sync']:
                self.log_error('push to github')
                subprocess.call(['cd "%s" && git push github master' % repo['path']], shell=True)

        except Exception as e:
            logger.error("Deploy error: %s", e)

    def respond(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def parse_request(self):
        length = int(self.headers.getheader('content-length'))
        body = self.rfile.read(length)
        payload = json.loads(body)
        return payload['repository']['url']

    def match_repository(self, git):
        with open('repository.json') as f:
            try:
                repositories = json.loads(f.read())
                for repository in repositories:
                    if git == repository['git']:
                        return repository

            except Exception as e:
                logger.error("Unmarshal repository.json fail: %s", e)

        return None


def main():
    host_port = ('127.0.0.1', 27001)
    logger.info("AutoDeploy Service start on %s", host_port)
    server = BaseHTTPServer.HTTPServer(host_port, AutoDeployHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
