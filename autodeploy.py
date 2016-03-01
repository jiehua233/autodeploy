#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os.path
import BaseHTTPServer
import sh
from sh import git


REPOSITORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'repository.json')

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

        git_url = self.get_git_url()
        repository = self.match_repository(git_url)
        self.deploy(repository)

    def deploy(self, repository):
        logger.info("Processing %s", repository["git"])
        try:
            logger.info("Changing working directory to %s", repository["path"])
            sh.cd(repository["path"])
            # 更新代码
            logger.info("Updating code, git pull origin")
            git.pull("origin", _out=logger.info, _err=logger.error)
            # 清除已删除的分支
            logger.info("Deleting old branches, git fetch -p")
            git.fetch("origin", "-p", _out=logger.info, _err=logger.error)

            # 同步到github
            if repository['sync']:
                logger.info("Syncing to github, git push github")
                git.push("github", _out=logger.info, _err=logger.error, _bg=True)

        except Exception as e:
            logger.error("Deploy error: %s", e)

    def respond(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def get_git_url(self):
        length = int(self.headers.getheader('content-length'))
        body = self.rfile.read(length)
        payload = json.loads(body)
        return payload['repository']['url']

    def match_repository(self, git):
        with open(REPOSITORY) as f:
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
    logger.info("AutoDeploy Service start on %s:%s" % host_port)
    server = BaseHTTPServer.HTTPServer(host_port, AutoDeployHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
