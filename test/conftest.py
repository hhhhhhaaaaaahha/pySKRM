import pytest
from pyskrm import SKRM

# 工廠：每次呼叫回傳一個新的 SKRM，避免狀態汙染
@pytest.fixture
def skrm_factory():
    def _make(word_size=8, num_words=2, strategy="naive", num_racetrack=1, num_overhead=2):
        return SKRM(word_size=word_size,
                    num_words=num_words,
                    num_racetrack=num_racetrack,
                    strategy=strategy,
                    num_overhead=num_overhead)
    return _make

# 常用的三種策略，各自一個乾淨實例（function-scope，預設）
@pytest.fixture
def skrm_naive(skrm_factory):
    return skrm_factory(strategy="naive")

@pytest.fixture
def skrm_pw(skrm_factory):
    return skrm_factory(strategy="pw")

@pytest.fixture
def skrm_pw_plus(skrm_factory):
    # 注意：pw_plus 內部會把 word_size + 1
    return skrm_factory(strategy="pw_plus")

# 自動套用：關閉計算/摘要時的 print 噪音（若你有測這些方法）
@pytest.fixture(autouse=True)
def _silence_print(monkeypatch):
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
