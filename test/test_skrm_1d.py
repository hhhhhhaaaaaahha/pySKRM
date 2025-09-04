import types
import pytest

from pyskrm.skrm import SKRM

# Using self-defined error; if missing, roll back to Exception
try:
    from pyskrm.argument_error import ArgumentError
except Exception:  # pragma: no cover
    ArgumentError = Exception


def test_storage_size_scales_with_racetrack(make_skrm):
    """驗證 racetrack 數量對 storage 長度的線性放大。"""
    s1 = make_skrm(num_racetrack=1)
    s4 = make_skrm(num_racetrack=4)
    assert len(s4.storage) == 4 * len(s1.storage)

def test_invalid_strategy(make_skrm):
    with pytest.raises(ArgumentError) as excinfo:
        make_skrm(word_size=32, num_words=3, strategy='')
    assert "Invalid update strategy." in str(excinfo.value)

def test_primitive_operations_boundary_and_visualize(make_skrm):
    s = make_skrm(word_size=32, num_words=3)

    s.inject(0)
    assert s.render_visualization() == "00000000000000000000000000000000 |1| 00000000000000000000000000000000 |0| 00000000000000000000000000000000 |0| 00000000000000000000000000000000 |0| 00000000000000000000000000000000\n"

    s.inject(3)
    assert s.render_visualization() == "00000000000000000000000000000000 |1| 00000000000000000000000000000000 |0| 00000000000000000000000000000000 |0| 00000000000000000000000000000000 |1| 00000000000000000000000000000000\n"

    assert s.detect(0) == 1
    assert s.detect(1) == 0
    assert s.detect(2) == 0
    assert s.detect(3) == 1

    s.remove(0)
    assert s.render_visualization() == "00000000000000000000000000000000 |0| 00000000000000000000000000000000 |0| 00000000000000000000000000000000 |0| 00000000000000000000000000000000 |1| 00000000000000000000000000000000\n"
    assert s.detect(0) == 0

    s.inject(1)
    s.shift(3, 2)
    assert s.render_visualization() == "00000000000000000000000000000000 |0| 00000000000000000000000000000000 |1| 00000000000000000000000000000000 |0| 00000000000000000000000000000001 |0| 00000000000000000000000000000000\n"
    s.shift(0, 1)
    assert s.render_visualization() == "00000000000000000000000000000000 |0| 00000000000000000000000000000000 |0| 00000000000000000000000000000000 |0| 00000000000000000000000000000001 |0| 00000000000000000000000000000000\n"


    # Inject out-of-bound
    with pytest.raises(ArgumentError) as excinfo:
        s.inject(-1)
    assert "AP must be must be between 0 and num_words." in str(excinfo.value)
    with pytest.raises(ArgumentError) as excinfo:
        s.inject(4)
    assert "AP must be must be between 0 and num_words." in str(excinfo.value)
    
    # Detect out-of-bound
    with pytest.raises(ArgumentError) as excinfo:
        s.detect(-1)
    assert "AP must be must be between 0 and num_words." in str(excinfo.value)
    with pytest.raises(ArgumentError) as excinfo:
        s.detect(4)
    assert "AP must be must be between 0 and num_words." in str(excinfo.value)
    
    # Remove out-of-bound
    with pytest.raises(ArgumentError) as excinfo:
        s.remove(-1)
    assert "AP must be must be between 0 and num_words." in str(excinfo.value)
    with pytest.raises(ArgumentError) as excinfo:
        s.remove(4)
    assert "AP must be must be between 0 and num_words." in str(excinfo.value)
    
    # Shift out-of-bound
    with pytest.raises(ArgumentError) as excinfo:
        s.shift(-1, 2)
    assert "AP must be must be between 0 and num_words." in str(excinfo.value)
    with pytest.raises(ArgumentError) as excinfo:
        s.shift(2, -1)
    assert "AP must be must be between 0 and num_words." in str(excinfo.value)
    with pytest.raises(ArgumentError) as excinfo:
        s.shift(0, 4)
    assert "AP must be must be between 0 and num_words." in str(excinfo.value)
    with pytest.raises(ArgumentError) as excinfo:
        s.shift(4, 0)
    assert "AP must be must be between 0 and num_words." in str(excinfo.value)

    # Shift between single AP
    with pytest.raises(ArgumentError) as excinfo:
        s.shift(2, 2)
    assert "The access ports of shift operation can not be the same." in str(excinfo.value)

@pytest.mark.parametrize("strategy,ws_delta", [
    ("naive", 0),
    ("pw", 0),
    ("pw_plus", 1),
])
def test_word_size_adjusts_by_strategy(make_skrm, strategy, ws_delta):
    base = 32
    s = make_skrm(word_size=base, strategy=strategy)
    assert s.word_size == base + ws_delta

def test_write_bound_and_callable(skrm_each_strategy):
    """三種策略都應該把 write 綁成 bound method 且可被呼叫。"""
    s, strategy = skrm_each_strategy
    assert strategy in ["naive", "pw", "pw_plus"]
    assert isinstance(s.write, types.MethodType)
    assert s.write.__self__ is s
    # smoke run（不驗證內部細節，僅確保不拋例外）
    s.write(0.125, 0)

def test_operation_count_of_update_under_strategies(skrm_each_strategy):
    s, strategy = skrm_each_strategy
    assert strategy in ["naive", "pw", "pw_plus"]

    i0, d0, r0, sh0 = s.inject_count, s.detect_count, s.remove_count, s.shift_count
    assert i0 == 0
    assert d0 == 0
    assert r0 == 0
    assert sh0 == 0

    s.write(0.125, 0)
    s.visualize()
    i1, d1, r1, sh1 = s.inject_count, s.detect_count, s.remove_count, s.shift_count
    if strategy == "naive":
        assert i1 == 5
        assert d1 == 0
        assert r1 == 32
        assert sh1 == 64
    elif strategy == "pw":
        assert i1 == 5
        assert d1 == 32
        assert r1 == 0
        assert sh1 == 66
    else:
        assert i1 == 5
        assert d1 == 33
        assert r1 == 1
        assert sh1 == 65
    
    s.write(0.124, 0)
    i2, d2, r2, sh2 = s.inject_count, s.detect_count, s.remove_count, s.shift_count
    if strategy == "naive":
        assert i2 == i1 + 23
        assert d2 == d1 + 0
        assert r2 == r1 + 32
        assert sh2 == sh1 + 64
    elif strategy == "pw":
        assert i2 == i1 + 18
        assert d2 == d1 + 32
        assert r2 == r1 + 0
        assert sh2 == sh1 + 66
    else:
        assert i2 == i1 + 5
        assert d2 == d1 + 33
        assert r2 == r1 + 1
        assert sh2 == sh1 + (68 - 0) # 0: Index of flip-bit
    
    s.write(0.125, 0)
    i3, d3, r3, sh3 = s.inject_count, s.detect_count, s.remove_count, s.shift_count

    if strategy == "naive":
        assert i3 == i2 + 5
        assert d3 == d2 + 0
        assert r3 == r2 + 32
        assert sh3 == sh2 + 64
    elif strategy == "pw":
        assert i3 == i2 + 0
        assert d3 == d2 + 32
        assert r3 == r2 + 18
        assert sh3 == sh2 + 66 + 18
    else:
        assert i3 == i2 + 0
        assert d3 == d2 + 12
        assert r3 == r2 + 33 + 1
        assert sh3 == sh2 + (68 - 21) # 0: Index of flip-bit
