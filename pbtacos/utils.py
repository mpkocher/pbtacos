import logging
import sys
import glob
import os


def cellPathFromLimsCode(limsCode):
    globRoot = '/mnt/data*/vol*/%s/%s'
    subVals = tuple(limsCode.split('-'))
    if len(subVals) == 2:
        globVal = glob.glob(globRoot % subVals)
        if globVal and len(globVal) == 1:
            return globVal[0]

    return None


def is_astro_dir(path):
    """
    The path should include the primary analysis folder

    If the root dir has the *.avi and *.metadata.xml file
    and the
    """
    # is this required?
    p0 = glob.glob(os.path.join(path, '..', '*.avi'))

    p1 = glob.glob(os.path.join(path, "*.bas.h5"))
    p2 = glob.glob(os.path.join(path, "..", "*.metadata.xml"))
    return all(len(x) != 0 for x in [p1, p2, p0])
