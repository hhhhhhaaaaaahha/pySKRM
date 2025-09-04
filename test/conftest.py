import os
import sys
import pytest

from pyskrm import SKRM

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

@pytest.fixture
def make_skrm():
    """Factory: Use make_skrm(strategy='pw_plus', num_racetrack=4, ...) to construct SKRM。"""
    def _make(**kw):
        params = dict(word_size=32, num_words=3, strategy="naive")
        params.update(kw)
        return SKRM(**params)
    return _make

@pytest.fixture(params=["naive", "pw", "pw_plus"])
def skrm_each_strategy(make_skrm, request):
    """The instances of three strategies of SKRM"""
    return make_skrm(strategy=request.param), request.param
