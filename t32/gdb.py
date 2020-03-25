# This can only run inside gdb
from __future__ import absolute_import
import gdb
import sys
import shlex

from .base import T32Interface

class T32GdbMonitorInterface(T32Interface):
    def run(self, args):
        if isinstance(args, list):
            args = ' '.join(args)
        gdb.execute('monitor B::' + args)

    def eval(self, args):
        if isinstance(args, list):
            args = ' '.join(args)
        gdb.execute('monitor eval B::' + args)

class T32RemGdbCommand(gdb.Command):
    def __init__(self):
        super(T32RemGdbCommand, self).__init__("t32rem", gdb.COMMAND_NONE)
        self.t32mon = T32GdbMonitorInterface()

    def invoke(self, arg, from_tty):
        self.t32mon.run(arg)

T32RemGdbCommand()

class T32GdbCommand(gdb.Command):
    def __init__(self):
        super(T32GdbCommand, self).__init__("t32", gdb.COMMAND_NONE)

    def invoke(self, arg, from_tty):
        t32 = T32GdbMonitorInterface()
        from .__main__ import invoke
        invoke(shlex.split(arg), t32)

T32GdbCommand()
