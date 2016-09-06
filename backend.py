#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @author:  jiehua233@gmail.com
# @site:    http://chenjiehua.me
# @date:    2016-09-07
#

from celery import Celery
import config

app = Celery(config.backend["name"], broker=config.backend["broker"])
if config.backend.get("conf"):
    app.conf.update(config.backend["conf"])


if __name__ == "__main__":
    app.start()
