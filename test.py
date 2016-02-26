#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

repos = [
    {
        "git": "git@git.chenjiehua.me:wiki/awesome-wiki.git",
        "path": "/home/ubuntu/vhost/",
        "github": True,
    },
    {
        "git": "git@git.chenjiehua.me:API/doc.git",
        "path": "/home/ubuntu/vhost/",
        "github": True,
    },
]

print json.dumps(repos)
