#!/usr/bin/env python
import os
import logging
import tempfile
import subprocess

from collections import OrderedDict
from xml.etree.ElementTree import ElementTree, ParseError


log = logging.getLogger(__name__)


def local(cmd):
    return subprocess.check_call(cmd, shell=True)



class SGEJob(object):

    def __init__(self, idx, name, user, state, queue_name, slots):
        self.idx = idx
        self.name = name
        self.user = user
        self.state = state
        self.queue_name = queue_name
        self.nslots = slots

    def __repr__(self):
        _d = dict(k=self.__class__.__name__, i=self.idx, u=self.user,
                  s=self.state, n=self.nslots, q=self.queue_name, x=self.name)
        return "<{k} {i} nslots:{n} user:{u} state:{s} queue:{q} {x} >".format(**_d)


def get_job_state_from_qstat(job_id):
    cmd = "qstat -j {x}".format(x=job_id)
    p = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.communicate()
    return out


def kill_job(job):
    local("qdel {i}".format(i=job.idx))


def kill_all_my_jobs():
    jobs = get_jobs_by_user('mkocher')
    for job in jobs:
        kill_job(job)


def get_jobs_by_me():
    return get_jobs_by_user('mkocher')


def _validate_resource(func, path):
    if func(path):
        return os.path.abspath(path)
    else:
        raise IOError("Unable to find {f}".format(f=path))


def get_job_dir(system_base_dir, job_id):
    # FIXME. Update to SA3
    b = str(job_id).rjust(6, '0')
    return os.path.join(system_base_dir, 'common', 'jobs', b[:3], b)


def _get_data(e, element_name):
    x = e.find(element_name)
    v = x.text
    return v


def __get_data_with_type(e, element_name, type_):
    return type_(_get_data(e, element_name))


def __get_jobs_from_xml_node(xml_node_iter):
    job_attrs = OrderedDict([('JB_job_number', int),
                             ('JB_name', str),
                             ('JB_owner', str),
                             ('state', str),
                             ('queue_name', str),
                             ('slots', int)])
    sge_jobs = []
    for ji in xml_node_iter:
        attrs = []
        for element_name, etype in job_attrs.iteritems():
            v = __get_data_with_type(ji, element_name, etype)
            attrs.append(v)
        job = SGEJob(*attrs)
        sge_jobs.append(job)

    return sge_jobs


def _parse_qstat_xml(file_name):

    et = ElementTree(file=file_name)

    r = et.getroot()
    # get all running jobs
    qis = r.findall('queue_info')
    qi = qis[0]
    jis = qi.findall('job_list')

    # get all jobs in the queue
    wis = r.findall('job_info')
    wi = wis[0]
    wjis = wi.findall('job_list')

    sge_jobs = __get_jobs_from_xml_node(jis)
    wsge_jobs = __get_jobs_from_xml_node(wjis)
    return sge_jobs + wsge_jobs


def _to_qstat_command(output_file, user=None):
    """Generate a qstat command to supplied output_file"""
    u = "*" if user is None else user
    cmd = 'qstat -u "{u}" -xml > {o}'.format(u=u, o=output_file)
    return cmd


def get_jobs_by_user(user_name):
    return get_jobs(user=user_name)


def get_jobs(user=None):
    """Get the current SGE jobs """
    f = tempfile.NamedTemporaryFile(suffix="_qstat.xml", delete=False)
    f.close()
    qstat_xml = f.name
    cmd = _to_qstat_command(qstat_xml, user=user)

    local(cmd)

    try:
        sge_jobs = _parse_qstat_xml(qstat_xml)
    except ParseError:
        log.warn("Unable to get qstat jobs")
        sge_jobs = []

    if os.path.exists(qstat_xml):
        os.remove(qstat_xml)

    return sge_jobs


def filter_jobs_by(funcs, jobs):
    f_jobs = []
    for job in jobs:
        if all(not func(job) for func in funcs):
            f_jobs.append(job)

    return f_jobs


def jobs_summary(jobs):

    users = {job.user for job in jobs}

    states = {job.state for job in jobs}

    ujust = 20
    outs = []
    state_str = " ".join(["{} (slots) ".format(state).rjust(10) for state in states])
    state_pad = 6
    outs.append(" ".join(["Users".ljust(ujust), "Total Jobs".ljust(10), state_str]))
    outs.append('-' * (len(outs[0]) + 6))
    for user in users:
        user_jobs = [job for job in jobs if job.user == user]
        out = [user.ljust(ujust), str(len(user_jobs)).ljust(10)]
        for state in states:
            state_jobs = [j for j in user_jobs if j.state == state]
            nslots = sum(j.nslots for j in state_jobs)
            x = "".join(['(', str(nslots), ')'])
            s = " ".join([str(len(state_jobs)).ljust(state_pad), x.ljust(state_pad)])
            out.append(s.ljust(10))

        outs.append(" ".join([str(o) for o in out]))

    return "\n".join(outs)


def jobs_to_dataframe(jobs):
    import pandas as pd

    d = []
    attr_names = ['idx', 'nslots', 'user', 'state', 'queue_name', 'name']
    for job in jobs:
        x = {a: getattr(job, a) for a in attr_names}
        d.append(x)

    df = pd.DataFrame(d)
    return df
