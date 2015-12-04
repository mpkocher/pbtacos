import os

from .servers import PortalServer, Server, MilhouseServer, SmrtLinkServer

_BUILD_ROOT = os.path.expanduser('~/builds')
_PYSIV_ROOT = os.path.expanduser('~/dev_pysiv/Pysiv')
_PYSIV_JOBS = os.path.join(_PYSIV_ROOT, 'jobs')

PORTAL_INTERNAL = PortalServer('portal.internal', 'http://smrtportal-internal', 2010, '/mnt/secondary/iSmrtanalysis/current')
# mp-f017
PORTAL_BETA = PortalServer('portal.beta', 'http://smrtportal-beta', 8000, '/mnt/secondary/Smrtanalysis/current')
PORTAL_SIV3 = PortalServer('portal.siv3', 'http://siv3', 8000, '/mnt/secondary-siv/nightlytest/siv3/smrtanalysis/current')
PORTAL_SIV4 = PortalServer('portal.siv4', 'http://siv4', 8000, '/mnt/secondary-siv/nightlytest/siv4/smrtanalysis/current')

_PORTAL_SYSTEMS = [PORTAL_INTERNAL, PORTAL_SIV4, PORTAL_SIV3, PORTAL_BETA]
PORTAL_SYSTEMS = {s.idx: s for s in _PORTAL_SYSTEMS}

MILHOUSE_ALPHA = MilhouseServer('milhouse.alpha', 'http://mp-f027', 8000, '')
MILHOUSE_DEV = MilhouseServer('milhouse.dev', 'http://milhouse', 9999, '/mnt/secondary/Share/Milhouse2/dev')
MILHOUSE_PROD = MilhouseServer('milhouse.prod', 'http:/milhouse', 8000, '/mnt/esecondary/Share/Milhouse2/prod')

_MILHOUSE_SYSTEMS = [MILHOUSE_ALPHA, MILHOUSE_DEV, MILHOUSE_PROD]
MILHOUSE_SYSTEMS = {s.idx: s for s in _MILHOUSE_SYSTEMS}

SL_BETA = SmrtLinkServer("smrtlink-beta", "http://smrtlink-beta", 8081, "/pbi/dept/secondary/siv/smrtlink/smrtlink-beta/smrtsuite/userdata/jobs_root")

SL_NIGHTLY = SmrtLinkServer("smrtlink-beta", "http://smrtlink-beta", 8081, "/pbi/dept/secondary/siv/smrtlink/smrtlink-nightly/smrtsuite/userdata/jobs_root")

SL_ALPHA = SmrtLinkServer("smrtlink-beta", "http://smrtlink-beta", 8081, "/pbi/dept/secondary/siv/smrtlink/smrtlink-alpha/smrtsuite/userdata/jobs_root")

SL_BIHOURLY = SmrtLinkServer("smrtlink-beta", "http://smrtlink-beta", 8081, "/pbi/dept/secondary/siv/smrtlink/smrtlink-bihourly/smrtsuite/userdata/jobs_root")