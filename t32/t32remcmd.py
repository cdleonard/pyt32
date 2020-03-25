import subprocess
import time
import logging
import shlex
logger = logging.getLogger(__name__)

from .base import T32Interface

_MSG_TEMPINFO = 'command returned Temporary Information, message: '

class T32RemCmdInterface(T32Interface):
    """Interface with Trace32 by running the t32rem binary"""

    def __init__(self, t32remcmd=['t32rem'], host='localhost'):
        self.t32remcmd = t32remcmd
        self.host = host

    def run(self, cmd, capture_output=None, check=True):
        cmd = self.t32remcmd + [self.host] + cmd
        kw = dict(check=check)

        if capture_output:
            kw['stdout'] = subprocess.PIPE
            kw['stderr'] = subprocess.PIPE
            kw['universal_newlines'] = True

        logger.info("RUN: %s", shlex.quote(cmd))
        return subprocess.run(cmd, **kw)

    def echo(self, *args):
        res = self.run(['ECHO'] + list(args), capture_output=True)
        if res.stdout.startswith(_MSG_TEMPINFO):
            echoval = res.stdout[len(_MSG_TEMPINFO):].rstrip('\n')
        else:
            raise Exception("Failed to parse t32rem output {!r}".format(res.stdout))

        from . import parse_t32_echo
        return parse_t32_echo(echoval)
