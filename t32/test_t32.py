import pytest

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

@pytest.fixture
def t32(request):
    if request.param == 'rem':
        from .t32remcmd import T32RemCmdInterface
        return T32RemCmdInterface()
    elif request.param == 'dll':
        from .ctypes import T32CtypesInterface
        return T32CtypesInterface()
    else:
        raise Exception()

def pytest_generate_tests(metafunc):
    if 't32' in metafunc.fixturenames:
        vals = []
        if metafunc.config.getoption('test_t32rem_interface', False):
            vals.append('rem')
        if metafunc.config.getoption('test_t32dll_interface', False):
            vals.append('dll')
        metafunc.parametrize("t32", vals, indirect=True, scope='module')
