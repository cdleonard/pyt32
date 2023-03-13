import os
import shutil
import pytest
from . import parse_t32_echo

def test_parse_t32_echo():
    assert parse_t32_echo("123.") == 123
    assert parse_t32_echo("0x42") == 0x42

def test_t32_echo_true(t32):
    assert t32.echo('True()') is True

def test_t32_echo_false(t32):
    assert t32.echo('False()') is False

def test_t32_echo_int(t32):
    assert t32.echo('1+1') == 2

def test_t32_echo_int_dec(t32):
    assert t32.echo('123.+456.') == 579

def test_t32_echo_int_hex(t32):
    assert t32.echo('0x123+0x456') == 0x579

def create_t32rem():
    if not shutil.which("t32rem"):
        pytest.skip("Missing t32rem in PATH")
    from .t32remcmd import T32RemCmdInterface
    return T32RemCmdInterface()

def create_t32api():
    from . import T32NotFoundException
    from .ctypes import T32CtypesInterface
    try:
        return T32CtypesInterface()
    except T32NotFoundException as e:
        pytest.skip(f"Skip T32API: {e}")

@pytest.fixture
def t32(request):
    if request.param == 'rem':
        return create_t32rem()
    elif request.param == 'dll':
        return create_t32api()
    else:
        raise Exception()

def pytest_generate_tests(metafunc):
    if 't32' in metafunc.fixturenames:
        vals = ["rem", "dll"]
        metafunc.parametrize("t32", vals, indirect=True, scope='module')
