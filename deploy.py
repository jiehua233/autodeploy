#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @author:  jiehua233@gmail.com
# @site:    http://chenjiehua.me
# @date:    2016-09-07
#

import os
import os.path
import logging
import ConfigParser
import sh
from sh import git
from StringIO import StringIO
from backend import app
from config import project_root


@app.task
def process(target):
    repos = get_repos_list()
    for repo in repos:
        if repo == target:
            deploy_code(repos[repo])
            break


def get_repos_list():
    repos = {}
    for root, dirs, files in os.walk(project_root):
        if ".git" in dirs:
            project_path = os.path.join(project_root, root)
            git_config = os.path.join(project_path, ".git/config")
            origin, back2github = parse_git_config(git_config)
            repos.setdefault(origin, {"dir": project_path, "sync": back2github})
            del dirs[:]

    return repos


def parse_git_config(git_config):
    with open(git_config) as f:
        c = f.readlines()

    config_parser = ConfigParser.ConfigParser()
    # ConfigParser cannot be used directly due to the leading spaces in git config file
    config_parser.readfp(StringIO("".join([l.lstrip() for l in c])))
    back2github = config_parser.has_section('remote "github"')
    origin = config_parser.get('remote "origin"', "url") \
        if config_parser.has_section('remote "origin"') \
        and config_parser.has_option('remote "origin"', "url") \
        else None

    return origin, back2github


def deploy_code(repo):
    logging.info("Deploying repo: %s, back2github: %s", repo["dir"], repo["sync"])
    try:
        logging.info("Change working directory to %s", repo["dir"])
        sh.cd(repo["dir"])
        logging.info("Update code, git pull origin")
        git.pull("origin", _out=logging.info, _err=logging.error)
        logging.info("done")
        logging.info("Delete old branches, git fetch -p")
        git.fetch("origin", "-p", _out=logging.info, _err=logging.error)
        logging.info("done")

        if repo["sync"]:
            logging.info("Back2github, git push github")
            git.push("github", _out=logging.info, _err=logging.error, _bg=True)

    except Exception as e:
        logging.info("Deploy error: %s", e)
