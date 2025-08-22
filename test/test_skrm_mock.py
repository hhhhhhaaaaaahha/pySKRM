import pytest
from pyskrm import SKRM

def make_pattern_len(length, kind="alt"):
    if kind == "alt":
        return "".join("1" if i % 2 == 0 else "0" for i in range(length))
    if kind == "head1":
        return "1" + "0" * (length - 1)
    if kind == "mid1":
        mid = max(1, length // 3)
        return "0" * mid + "1" + "0" * (length - mid - 1)
    if kind == "all0":
        return "0" * length
    if kind == "all1":
        return "1" * length
    raise ValueError("unknown kind")

def test_naive_write_exact_counts_with_mock(monkeypatch):
    skrm = SKRM(word_size=8, num_words=2, strategy="naive")
    pattern = make_pattern_len(skrm.word_size, "alt")
    monkeypatch.setattr("pyskrm.skrm.convert_float_to_ieee754_single",
                        lambda number, *a, **k: pattern)
    skrm.naive_write(0.0, target_word=0)
    assert skrm.remove_count == skrm.word_size
    assert skrm.shift_count == 2 * skrm.word_size
    assert skrm.inject_count == pattern.count("1")
    assert skrm.detect_count == 0

@pytest.mark.parametrize("kind", ["all0", "all1", "mid1"])
def test_permutation_write_with_mock(monkeypatch, kind):
    skrm = SKRM(word_size=8, num_words=2, strategy="pw")
    pattern = make_pattern_len(skrm.word_size, kind)
    monkeypatch.setattr("pyskrm.skrm.convert_float_to_ieee754_single",
                        lambda number, *a, **k: pattern)
    skrm.permutation_write(1.23, target_word=0)
    assert skrm.inject_count <= pattern.count("1")
    assert skrm.shift_count >= skrm.word_size
    assert skrm.detect_count >= 1
    assert skrm.remove_count >= 0

@pytest.mark.parametrize("kind", ["head1", "mid1", "all1"])
def test_pw_plus_with_mock(monkeypatch, kind):
    base_word_size = 8
    skrm = SKRM(word_size=base_word_size, num_words=2, strategy="pw_plus")
    pattern = make_pattern_len(skrm.word_size, kind)
    def _mock(number, *a, **k):
        return pattern
    monkeypatch.setattr("pyskrm.skrm.convert_float_to_ieee754_single", _mock)
    skrm.pw_plus(0.75, target_word=0)
    assert skrm.shift_count >= 1
    assert skrm.remove_count >= 0
    assert skrm.inject_count <= pattern.count("1")

def test_all_zero_patterns_do_not_inject(monkeypatch):
    for strategy in ("naive", "pw", "pw_plus"):
        skrm = SKRM(word_size=8, num_words=2, strategy=strategy)
        pattern = "0" * skrm.word_size
        monkeypatch.setattr("pyskrm.skrm.convert_float_to_ieee754_single",
                            lambda number, *a, **k: pattern)
        if strategy == "naive":
            skrm.naive_write(0.0, 0)
        elif strategy == "pw":
            skrm.permutation_write(0.0, 0)
        else:
            skrm.pw_plus(0.0, 0)
        assert skrm.inject_count == 0
