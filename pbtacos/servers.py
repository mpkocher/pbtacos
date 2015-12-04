#!/usr/bin/env python
import os
import sys
import logging
import tempfile
import subprocess
import glob
import urlparse
import itertools
import functools

from collections import OrderedDict
from xml.etree.ElementTree import ElementTree, ParseError

import requests

from fabric.api import local
from fabric.context_managers import shell_env, lcd, prefix


class Server(object):

    def __init__(self, idx, url, port, root_dir):
        self.idx = idx
        self.url = url
        self.port = port
        self.root_dir = root_dir

    @property
    def url_port(self):
        return ":".join([self.url, str(self.port)])

    def __repr__(self):
        _d = dict(k=self.__class__.__name__,
                  i=self.idx,
                  u=self.url,
                  p=self.port,
                  d=self.root_dir)
        return "<{k} id:{i} {u}:{p} {d} >".format(**_d)


class PortalServer(Server):
    JOB_ROOT = 'common/jobs'

    def get_job_path_from_id(self, job_id):
        b = str(job_id).rjust(6, '0')
        p = b[:3]
        # might want to check a job
        job_path = os.path.join(self.root_dir, self.__class__.JOB_ROOT, p, b)
        return job_path


def _get_milhouse_status(url_with_port):
    """Get info from milhouse server"""
    try:
        u = urlparse.urljoin(url_with_port, "status")
        r = requests.get(u)
        j = r.json()
        return j['success'] == 'ok'
    except Exception:
        return False


class MilhouseServer(Server):
    JOB_ROOT = 'projects'

    def get_status(self):
        return _get_milhouse_status(self.url_port)


# def get_job_dir(server_base_id, job_id):
#     s = PORTAL_SYSTEMS[server_base_id]
#     b = str(job_id).rjust(6, '0')
#     return os.path.join(s.root_dir, 'common', 'jobs', b[:3], b)
#

class SmrtLinkServer(Server):
    # New post RS era
    # This has a different root dir interface

    def get_job_path_from_id(self, job_id):
        b = str(job_id).rjust(6, '0')
        p = b[:3]
        # might want to check a job
        job_path = os.path.join(self.root_dir, p, b)
        return job_path
