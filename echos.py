def bytearray2str(data: bytearray):
    #print("0x{0:0>2x}".format(a))
    return ",".join(["0x{0:0>2x}".format(n) for n in data])


def bytearray2ncecho(data: bytearray):
    return "".join([r"\x{0:0>2x}".format(n) for n in data])

if __name__ == "__main__":
    c = bytearray([n for n in range(10)])
    print(bytearray2ncecho(c))
    print(bytearray2str(c))
