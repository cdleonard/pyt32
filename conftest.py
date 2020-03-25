def pytest_addoption(parser):
    # See t32/test_t32.py
    parser.addoption("--test-t32rem-interface", action="store_true",
            help="test T32 interface based on t32rem")
    parser.addoption("--test-t32dll-interface", action="store_true",
            help="test T32 interface based on t32api.dll")
