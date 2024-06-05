def trunc_1byte(a: int):
    if a > 255:
        a = a%256
        return a.to_bytes(1, byteorder='little')
    else:
        return a.to_bytes(1, byteorder='little')    