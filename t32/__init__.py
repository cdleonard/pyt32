import os
from .base import T32Interface
from .t32remcmd import T32RemCmdInterface

# Compat alias
T32Rem = T32RemCmdInterface

def get_t32sys(default=None):
    val = os.getenv('T32SYS', default)
    if val is None:
        raise Exception('Missing T32SYS environment variable')
    return val

def parse_t32_echo(val):
    """Convert a string returned from T32 echo to typed python value

    Examples:

    >>> parse_t32_echo(".123")
    123
    >>> parse_t32_echo("FALSE()")
    False
    """
    if val == 'TRUE()':
        return True
    elif val == 'FALSE()':
        return False
    elif val.startswith('0x'):
        return int(val, 16)
    elif val.endswith('.'):
        return int(val[:-1], 10)
    else:
        return val

def get_t32(**kwargs):
    from .ctypes import T32CtypesInterface
    return T32CtypesInterface(**kwargs)
