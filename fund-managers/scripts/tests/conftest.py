"""engine-test 共享 fixture 与配置。"""

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # scripts/

DEFAULT_CODES = ["600519", "000858", "300750"]


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: 慢测试（网络/重I/O），默认跳过")


def pytest_addoption(parser):
    parser.addoption("--run-slow", action="store_true", default=False,
                     help="运行标记为 slow 的测试")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-slow"):
        return  # 不跳过 slow
    skip_slow = pytest.mark.skip(reason="需 --run-slow 参数运行")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(params=DEFAULT_CODES)
def stock_code(request):
    """参数化 fixture：对每只股票分别跑测试。"""
    return request.param
