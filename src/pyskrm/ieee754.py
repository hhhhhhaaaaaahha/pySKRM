import struct

def convert_float_to_ieee754_single(number: float, flip_bit: bool = False, precision:str = "single"):
    if precision == "single":
        # 32-bit IEEE 754
        packed = struct.pack('!f', number)
        bit_string = ''.join(f"{byte:08b}" for byte in packed)
    # elif precision == "double":
    #     # 64-bit IEEE 754
    #     packed = struct.pack('!d', number)
    #     bit_string = ''.join(f"{byte:08b}" for byte in packed)
    # else:
    #     raise ValueError("Precision should be 'single' or 'double.'")

    return bit_string if flip_bit == False else flip_ieee754(bit_string)

def flip_ieee754(ieee754: str, word_size: int = 32):
    if ieee754.count("1") > (word_size / 2):
        return "1" + ieee754.translate(str.maketrans("01", "10"))
    return "0" + ieee754