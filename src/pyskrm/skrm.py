from typing import Callable, Optional
from bitarray import bitarray

from .ieee754 import convert_float_to_ieee754_single
from .argument_error import ArgumentError


# Type alias for a write strategy function
WriteFn = Callable[["SKRM", float, int], None]

class SKRM():
    def __init__(self,
        word_size: int,
        num_words: int,
        num_racetrack: int = 1,
        strategy: str = 'naive',
        num_overhead: int = 2,
        write_fn: Optional[WriteFn] = None,
) -> None:
        # --- Validate/derive word size based on strategy semantics ---
        if strategy == 'pw_plus':
            self.word_size = word_size + 1
        elif strategy == 'naive' or strategy == 'pw':
            self.word_size = word_size
        else:
            raise ArgumentError("Invalid update strategy.")


        self.strategy = strategy
        self.num_words = num_words
        self.num_overhead = num_overhead

        # Storage layout: [ overhead | AP | word | AP | word | AP | ... | AP | overhead ] repeating on each racetrack
        self.storage = bitarray((self.word_size * (num_overhead + num_words) + num_words + 1) * num_racetrack)

        # Cost model (can be tuned externally if needed)
        self.inject_latency = 1
        self.detect_latency = 0.1
        self.remove_latency = 0.8
        self.shift_latency = 0.5

        self.inject_energy = 200
        self.detect_energy = 2
        self.remove_energy = 20
        self.shift_energy = 20

        self.inject_count = 0
        self.detect_count = 0
        self.remove_count = 0
        self.shift_count = 0

        # --- Strategy dispatch table (unbound functions) ---
        dispatch: dict[str, WriteFn] = {
            "naive": SKRM.naive_write,
            "pw": SKRM.permutation_write,
            "pw_plus": SKRM.pw_plus,
        }


        base_fn: WriteFn = write_fn if write_fn is not None else dispatch[strategy]
        # Bind to this instance -> becomes a bound method with `self`
        self.write: WriteFn = base_fn.__get__(self, SKRM) # type: ignore[assignment]


    # ---------- Primitive operations ----------
    def inject(self, ap: int):
        self.inject_count += 1
        self.storage[(self.word_size + 1) * (ap + 1) - 1] = 1
        
    def detect(self, ap: int):
        self.detect_count += 1
        return self.storage[(self.word_size + 1) * (ap + 1) - 1]

    def remove(self, ap: int):
        self.remove_count += 1
        self.storage[(self.word_size + 1) * (ap + 1) - 1] = 0

    def shift(self, start_ap: int, end_ap: int):
        if start_ap < end_ap:
            self.shift_count += 1
            self.storage[(self.word_size + 1) * (start_ap + 1) : (self.word_size + 1) * (end_ap + 1)] = self.storage[(self.word_size + 1) * (start_ap + 1) - 1 : (self.word_size + 1) * (end_ap + 1) - 1]
            self.storage[(self.word_size + 1) * (start_ap + 1) - 1] = 0
        elif end_ap < start_ap:
            self.shift_count += 1
            self.storage[(self.word_size + 1) * (end_ap + 1) - 1 : (self.word_size + 1) * (start_ap + 1) - 1] = self.storage[(self.word_size + 1) * (end_ap + 1) : (self.word_size + 1) * (start_ap + 1)]
            self.storage[(self.word_size + 1) * (start_ap + 1) - 1] = 0
        else:
            raise ArgumentError("The access ports of shift operation can not be the same.")

    # ---------- Convenience: swap out strategy at runtime ----------
    def set_write_fn(self, write_fn: WriteFn) -> None:
        """Replace the current write strategy with a new callable.
        Make sure your callable is compatible with the current layout.
        """
        self.write = write_fn.__get__(self, SKRM) # bind to instance

    # ---------- Visualization & accounting ----------
    def visualize(self):
        for idx, val in enumerate(self.storage):
            if idx % (self.word_size + 1) == self.word_size:
                print(f" |", end='')
            print(val, end='')
            if idx % (self.word_size + 1) == self.word_size:
                print(f"| ", end='')
        print("")

    def calculate_latency(self):
        inject_latency = self.inject_count * self.inject_latency
        detect_latency = self.detect_count * self.detect_latency
        remove_latency = self.remove_count * self.remove_latency
        shift_latency = self.shift_count * self.shift_latency

        print(f"Inject latency: {inject_latency: .1f}")
        print(f"Detect latency: {detect_latency: .1f}")
        print(f"Remove latency: {remove_latency: .1f}")
        print(f"Shift latency: {shift_latency: .1f}")
        print(f"----------------------")
        print(f"Total latency: {inject_latency + detect_latency + remove_latency + shift_latency: .1f}")

    def calculate_energy(self):
        inject_energy = self.inject_count * self.inject_energy
        detect_energy = self.detect_count * self.detect_energy
        remove_energy = self.remove_count * self.remove_energy
        shift_energy = self.shift_count * self.shift_energy

        print(f"Inject energy: {inject_energy}")
        print(f"Detect energy: {detect_energy}")
        print(f"Remove energy: {remove_energy}")
        print(f"Shift energy: {shift_energy}")
        print(f"----------------------")
        print(f"Total energy: {inject_energy + detect_energy + remove_energy + shift_energy}")

    def summarize(self):
        print(f"Inject count: {self.inject_count}")
        print(f"Detect count: {self.detect_count}")
        print(f"Remove count: {self.remove_count}")
        print(f"Shift count: {self.shift_count}")
        print(f"----------------------")
        self.calculate_latency()
        print(f"----------------------")
        self.calculate_energy()
    
    # ---------- Built-in strategies (kept as instance methods) ----------
    def naive_write(self, number: float, target_word: int):
        # Boundary test
        if target_word < 0 or target_word > self.num_words - 1:
            raise ArgumentError("Target word must be must be between 0 and (num_word - 1).")

        # Init value
        ieee_num = convert_float_to_ieee754_single(number)

        # Remove
        for _ in range(self.word_size):
            self.shift(target_word, target_word + 1)
            self.remove(target_word + 1)

        # Inject
        for c in ieee_num:
            if c == '1':
                self.inject(target_word + 1)
            self.shift(target_word + 1, target_word)

    def permutation_write(self, number: float, target_word: int):
        # Boundary test
        if target_word < 0 or target_word > self.num_words - 1:
            raise ArgumentError("Target word must be must be between 0 and (num_word - 1).")
        
        # Init value
        ieee_num = convert_float_to_ieee754_single(number)
        sky_cnt = 0

        # Assemble
        self.shift(target_word, target_word + 1)
        for _ in range(self.word_size):
            if self.detect(target_word + 1) == 1:
                sky_cnt += 1
            self.shift(target_word, target_word + 1)
        
        # Re-permute & inject
        for c in ieee_num:
            self.shift(target_word + 1, target_word)
            if c == '1':
                if sky_cnt > 0:
                    sky_cnt -= 1
                    self.storage[(self.word_size + 1) * (target_word + 2) - 1] = 1
                else:
                    self.inject(target_word + 1)
        self.shift(target_word + 1, target_word)
        # self.shift_count += 1 # Shift 1 bit to align word to interport

        # Remove extra skyrmions
        while sky_cnt > 0:
            self.shift_count += 1
            self.remove_count += 1
            sky_cnt -= 1

    def pw_plus(self, number: float, target_word: int):
        # Boundary test
        if target_word < 0 or target_word > self.num_words - 1:
            raise ArgumentError("Target word must be must be between 0 and (num_word - 1).")

        # Input info
        d: str = convert_float_to_ieee754_single(number, True)
        d_popcnt = d.count('1')
        d_bsr = d.find('1')

        # Init value
        sky_cnt = 0
        save_assemble = 0
        save_permute = d_bsr
        permute_removal = True

        # Assemble
        self.shift(target_word, target_word +1)  
        for i in range(self.word_size - 1, -1, -1):
            b = self.detect(target_word + 1)
            if b == 0:
                self.shift(target_word, target_word +1)
            else:
                self.shift(target_word, target_word +1)
                sky_cnt += 1
                if sky_cnt == d_popcnt:
                    save_assemble = i - 1
                    break   

        # Re-permute & inject
        idx_leftmost_bit = 0
        if save_assemble < save_permute:
            for i in range(save_assemble, -1, -1):
                self.remove(target_word + 1)
            idx_leftmost_bit = d_bsr
            permute_removal = False
        for i in range(idx_leftmost_bit, self.word_size):
            if d[i] == '0':
                self.shift(target_word + 1, target_word)
            else:
                if sky_cnt > 0:
                    self.shift(target_word + 1, target_word)
                    self.storage[(self.word_size + 1) * (target_word + 2) - 1] = 1
                    sky_cnt -= 1
                else:
                    self.shift(target_word + 1, target_word)
                    self.inject(target_word + 1)
            if permute_removal:
                self.remove(target_word)
        self.shift(target_word + 1, target_word)
        self.remove(target_word)