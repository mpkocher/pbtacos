import logging
import os
import datetime
from collections import namedtuple

from fabric.api import local
from fabric.context_managers import shell_env, lcd, prefix

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

BASE_BUILD_DIR = "/mnt/secondary/builds/full/3.0.0/pkg"
BASE_OUTPUT_DIR = "/home/UNIXHOME/mkocher/sa3"
CREATE_SH_EXE = 'create-sa3-setup'

SaBuild = namedtuple("SaBuild", "root_dir run_sh version created_at")


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def get_all_builds(root_dir):
    f = os.path.join
    d = os.path.isdir
    fx = lambda x: x.startswith("smrtanalysis_")
    return [f(root_dir, x) for x in os.listdir(root_dir) if fx(x)]


def get_most_recent_build_dir():
    return get_all_builds(BASE_BUILD_DIR)[-1]


def get_newest_build():
    d = get_most_recent_build_dir()
    version = d.split('_')[-1]
    run_sh = os.path.join(d, os.listdir(d)[0])
    created_at = modification_date(run_sh)
    return SaBuild(d, run_sh, version, created_at)


def extract_build_to(build, root_dest_dir):
    """:type build: SaBuild"""
    dir_name = os.path.join(root_dest_dir, build.version)
    if os.path.exists(dir_name):
        raise IOError("Build dir {d} exists. Unable to extract build {b} exists.".format(b=build, d=dir_name))
    os.mkdir(dir_name)

    with lcd(dir_name):
        local("bash {x}".format(x=build.run_sh))

    log.info("Extracted build {b} to {d}".format(b=build, d=dir_name))
    return dir_name


def extract_newest_build():
    b = get_newest_build()
    log.info("Get newest build {b}".format(b=b))
    extract_build_to(b, BASE_OUTPUT_DIR)
    return b


def call_setup_sh(root_build_dir):
    setup_sh = os.path.join(root_build_dir, 'setup.sh')
    d = os.path.join(root_build_dir, 'smrtanalysis')
    local("{e} {d} > {f}".format(d=d, f=setup_sh, e=CREATE_SH_EXE))
    return setup_sh


def generate_newest_sh(root_dir):
    fs = [os.path.join(root_dir, p) for p in os.listdir(root_dir) if p.startswith("3.0.0")]
    sfs = sorted(fs)
    return call_setup_sh(sfs[-1])
