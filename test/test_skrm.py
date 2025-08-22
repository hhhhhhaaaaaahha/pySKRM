import pytest
from pyskrm import SKRM
from pyskrm.argument_error import ArgumentError

def test_init_invalid_strategy():
    with pytest.raises(ArgumentError):
        SKRM(word_size=8, num_words=4, strategy="invalid")

def test_inject_detect_counts(skrm_naive):
    skrm = skrm_naive
    skrm.inject(0)
    assert skrm.detect(0) == 1
    assert (skrm.inject_count, skrm.detect_count) == (1, 1)

def test_remove(skrm_naive):
    skrm = skrm_naive
    skrm.inject(0)
    skrm.remove(0)
    assert skrm.detect(0) == 0
    assert skrm.remove_count == 1

def test_shift_forward_changes_storage(skrm_factory):
    skrm = skrm_factory(word_size=4, num_words=2)
    skrm.inject(0)
    before = skrm.storage.copy()
    skrm.shift(0, 1)
    assert skrm.shift_count == 1
    assert before != skrm.storage

def test_shift_backward_changes_storage(skrm_factory):
    skrm = skrm_factory(word_size=4, num_words=2)
    skrm.inject(1)
    before = skrm.storage.copy()
    skrm.shift(1, 0)
    assert skrm.shift_count == 1
    assert before != skrm.storage

def test_shift_same_ap_raises(skrm_factory):
    skrm = skrm_factory(word_size=4, num_words=2)
    with pytest.raises(ArgumentError):
        skrm.shift(1, 1)

@pytest.mark.parametrize("strategy, method, number", [
    ("naive", "naive_write", 3.14),
    ("pw", "permutation_write", 2.71),
    ("pw_plus", "pw_plus", 1.23),
])
def test_write_paths_update_counters(skrm_factory, strategy, method, number):
    skrm = skrm_factory(strategy=strategy)
    getattr(skrm, method)(number, target_word=0)
    assert skrm.shift_count > 0

def test_visualize_runs_without_error(skrm_naive):
    skrm_naive.visualize()

def test_summarize_runs_without_error(skrm_pw):
    skrm = skrm_pw
    skrm.inject(0); skrm.detect(0); skrm.remove(0)
    skrm.shift(0, 1)
    skrm.summarize()

def test_pw_plus_specifics(skrm_pw_plus):
    skrm = skrm_pw_plus
    skrm.pw_plus(0.75, 0)
    assert skrm.shift_count >= 1
    assert skrm.remove_count >= 0

# # Test update from more to less
# print("Naive write:")
# test_skrm = SKRM(32, 3)
# test_skrm.visualize()
# print()

# test_skrm.naive_write(0.124, 1)
# test_skrm.visualize()
# print()

# test_skrm.naive_write(0.125, 1)
# test_skrm.visualize()
# print()

# test_skrm.summarize()

# print("\nPermutation-Write:")
# test_skrm = SKRM(32, 3, 1, 'pw')
# test_skrm.visualize()
# print()

# test_skrm.permutation_write(0.124, 1)
# test_skrm.visualize()
# print()

# test_skrm.permutation_write(0.125, 1)
# test_skrm.visualize()
# print()

# test_skrm.summarize()

# print("\nPW+:")

# test_skrm = SKRM(32, 3, 1, 'pw_plus')
# test_skrm.visualize()
# print()

# test_skrm.pw_plus(0.124, 1)
# test_skrm.visualize()
# print()

# test_skrm.pw_plus(0.125, 1)
# test_skrm.visualize()
# print()

# test_skrm.summarize()

# # Test update from less to more
# print("Naive write:")
# test_skrm = SKRM(32, 3)
# test_skrm.visualize()
# print()

# test_skrm.naive_write(0.125, 1)
# test_skrm.visualize()
# print()

# test_skrm.naive_write(0.124, 1)
# test_skrm.visualize()
# print()

# test_skrm.summarize()

# print("\nPermutation-Write:")

# test_skrm = SKRM(32, 3, 1, 'pw')
# test_skrm.visualize()
# print()

# test_skrm.permutation_write(0.125, 1)
# test_skrm.visualize()
# print()

# test_skrm.permutation_write(0.124, 1)
# test_skrm.visualize()
# print()

# test_skrm.summarize()

# print("\nPW+:")

# test_skrm = SKRM(32, 3, 1, 'pw_plus')
# test_skrm.visualize()
# print()

# test_skrm.pw_plus(0.125, 1)
# test_skrm.visualize()
# print()

# test_skrm.pw_plus(0.124, 1)
# test_skrm.visualize()
# print()

# test_skrm.summarize()