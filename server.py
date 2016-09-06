#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @author:  jiehua233@gmail.com
# @site:    http://chenjiehua.me
# @date:    2016-09-07
#

import logging
import falcon
import ujson as json
import deploy
from wsgiref import simple_server
from config import bind


class AutoDeploy(object):

    def on_get(self, req, resp):
        logging.error("test")
        resp.status = falcon.HTTP_200
        resp.body = "Gitlab auto deploy webhooks!"

    def on_post(self, req, resp):
        if req.headers.get("X-GITLAB-EVENT") != "Push Hook":
            resp.status = falcon.HTTP_304
            resp.body = "Only support push hook!"
            return

        resp.status = falcon.HTTP_200
        body = req.stream.read()
        if not body:
            logging.error("Empty req body!")
            return
        try:
            target = json.loads(body)["repository"]["url"]
        except Exception as e:
            logging.error("Json loads err: %s", e)
            return

        logging.info("Try to deploy %s", target)
        deploy.process.delay(target)


# logging init
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

app = falcon.API()
app.add_route("/", AutoDeploy())


if __name__ == "__main__":
    logging.info("Start server on %s", bind)
    host, port = bind.split(":")
    httpd = simple_server.make_server(host, int(port), app)
    httpd.serve_forever()
