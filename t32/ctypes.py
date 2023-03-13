import os
import sys
import enum
import time
import ctypes

import logging

from t32 import T32NotFoundException
logger = logging.getLogger(__name__)

from .base import T32Interface

# Arguments for T32_Attach
T32_DEV_OS = 0
T32_DEV_ICD = 1
T32_DEV_ICE = T32_DEV_ICD

T32_OK = 0

class PracticeState(enum.IntEnum):
    UNKNOWN     = -1
    NOT_RUNNING = 0
    RUNNING     = 1
    DIALOG_OPEN = 2

class T32MessageMode(enum.IntEnum):
    MessageModeNone       = 0x00
    MessageModeInfo       = 0x01
    MessageModeError      = 0x02
    MessageModeState      = 0x04
    MessageModeWarnInfo   = 0x08
    MessageModeErrorInfo  = 0x10
    MessageModeTemp       = 0x20
    MessageModeTempInfo   = 0x40

def format_t32_message(mode, msg):
    result = "command returned "

    if mode & 1:
            result += "General Information, "
    if mode & 2:
            result += "Error, "
    if mode & 8:
            result += "Status Information, "
    if mode & 16:
            result += "Error Information, "
    if mode & 32:
            result += "Temporary Display, "
    if mode & 64:
            result += "Temporary Information, "

    return result + 'message: ' + msg

def get_t32api_libname():
    """Auto-detect the correct library"""
    # Copy-pasted from t32 demos
    import platform
    psys = platform.system()

    if psys == 'Windows' or psys.startswith('CYGWIN'):
        if ctypes.sizeof(ctypes.c_voidp) == 4:
            return "t32api.dll"
        else:
            return "t32api64.dll"

    if psys == 'Darwin':
        return "t32api.dylib"

    if ctypes.sizeof(ctypes.c_voidp) == 4:
        return "t32api.so"
    else:
        return "t32api64.so"

class T32APINotFoundException(T32NotFoundException):
    pass

def get_t32api_libpath():
    """Get path to t32api libary as a string"""
    from . import get_t32sys
    t32sys = get_t32sys()
    libname = get_t32api_libname()
    for relpath in ['demo/api/capi/dll', 'demo/api/python']:
        result = os.path.join(t32sys, relpath, libname)
        if os.path.exists(result):
            return result
    raise T32APINotFoundException("Unable to find t32api library")

def get_t32api_dll(libpath=None):
    """Load t32api libary as a ctypes.CDLL"""
    if libpath is None:
        libpath = get_t32api_libpath()
    return ctypes.CDLL(libpath)

class T32CtypesInterface(T32Interface):
    """Interface with Trace32 via t32api library using ctypes"""

    def __init__(self, node='127.0.0.1', port=20000):
        self.t32api = get_t32api_dll()
        self.node = node
        self.port = port
        self._is_open = False
        self.open()

    def open(self):
        """Open connection to T32

        This calls T32_Config and T32_Init.

        Does nothing if already open (try to close first).
        """
        if self._is_open:
            return

        logger.debug("T32_Config...")
        self.t32api.T32_Config(b"NODE=", self.node.encode('ascii'))
        self.t32api.T32_Config(b"PORT=", str(self.port).encode('ascii'))
        self.t32api.T32_Config(b"PACKLEN=", b"1024")

        logger.debug("T32_Init...")
        err = self.t32api.T32_Init()
        if err:
            raise Exception("Failed T32_Init error %d" % (err,))

        self._is_open = True

    def close(self):
        """Close connection to T32

        This calls T32_Exit

        Dose nothing if not open
        """
        if not self._is_open:
            return

        logger.debug("T32_Exit")
        err = self.t32api.T32_Exit()
        if err:
            raise Exception("Failed T32_Exit error %d" % (err,))

        self._is_open = False

    def __enter__(self, *args):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        if self._is_open:
            logger.warning("closing t32 from destructor")
            self.close()

    def attach(self):
        """Run T32_Attach"""
        err = self.t32api.T32_Attach(T32_DEV_ICD)
        if err:
            raise Exception("Failed T32_Attach error %d" % (err,))

    def cmd(self, cmd):
        """Send a command with T32_Cmd"""
        if isinstance(cmd, list):
            cmd = ' '.join(cmd)
        logger.info("T32_Cmd %s", cmd)
        err = self.t32api.T32_Cmd(cmd.encode())
        if err:
            raise Exception("T32_Cmd error {} on {}".format(err, cmd))

    def run(self, cmd, wait_before=True, wait_after=True):
        """Run a TRACE32 command

        Default to maximum safety: wait for idle before and after

        :param wait_before: Call :py:func:wait: before running the command
        :param wait_before: Call :py:func:wait: after running the command
        """
        if wait_before:
            self.wait()
        self.cmd(cmd)
        if wait_after:
            self.wait()

    def wait(self):
        """Wait until T32_GetPracticeState is NOT_RUNNING"""
        state = ctypes.c_int(PracticeState.UNKNOWN)
        rc = 0
        while rc == 0 and not state.value == PracticeState.NOT_RUNNING:
            time.sleep(0.05)
            rc = self.t32api.T32_GetPracticeState(ctypes.byref(state))

    def dowait(self, args):
        """Send a command and wait for execution"""
        self.cmd(args)
        self.wait()

    def eval_string(self, args):
        self.cmd('EVAL ' + args)

        msg = ctypes.create_string_buffer(256)
        ret = self.t32api.T32_EvalGetString(msg)
        if ret < 0:
            raise Exception("T32_GetMessage error {}\n".format(ret))
        return msg.value.decode('utf8')

    def echo(self, args):
        self.cmd('ECHO ' + args)

        msg = ctypes.create_string_buffer(256)
        msgmode = ctypes.c_uint16()
        ret = self.t32api.T32_GetMessage(msg, ctypes.byref(msgmode))
        if ret < 0:
            raise Exception("T32_GetMessage error {}\n".format(ret))

        msg = msg.value.decode('utf8')
        logger.info('%s', format_t32_message(msgmode.value, msg))
        if msgmode.value == 0x40:
            from . import parse_t32_echo
            return parse_t32_echo(msg)
        else:
            raise Exception("ECHO returned unexpected msgmode 0x%x" % (msgmode.value))
