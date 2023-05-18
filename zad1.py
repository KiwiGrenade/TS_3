from warnings import warn

FLAG = "01111110"
GEN = "101"


def get_xor(x: str):
    res = ""
    for i in range(1, len(GEN)):
        if x[i] == GEN[i]:
            res += "0"
        else:
            res += "1"
    return res


def get_div_rem(data: str):
    next = len(GEN)
    rem = data[:next]
    while next <= len(data):
        if rem[0] == "1":
            rem = get_xor(rem)
        else:
            rem = rem[1:]
        if next == len(data):
            break
        rem += data[next]
        next += 1
    return rem


def crc(data: str):
    # add zeros
    data += "0" * (len(GEN) - 1)
    return get_div_rem(data)


def encode(data: str, max_datasize=32):
    frames = []
    i = 0

    while i < len(data):
        #
        cur = data[i: i + max_datasize]
        # append div_rem to data
        cur += crc(cur)
        frame_with_zeros = add_zeros(cur)

        frames.append(FLAG + frame_with_zeros + FLAG)
        i += max_datasize

    return "".join(frames)

def add_zeros(frame:str):
    no_zero_frame = ""
    ones = 0
    # add 0 after every fifth 1
    for c in frame:
        if ones == 5:
            ones = 0
            no_zero_frame += '0'
        if c == '1':
            ones += 1
        else:
            ones = 0
        no_zero_frame += c
    return no_zero_frame

def remove_zeros(frame: str):
    i = 0
    ones = 0
    zero_frame = ""
    while i < len(frame):
        zero_frame += frame[i]
        if frame[i] == "1":
            ones += 1
            if ones == 5:
                ones = 0
                i += 1
        else:
            ones = 0
        i += 1
    return zero_frame


def decode(data: str):
    # remove flags, create list of data
    frames = list(filter(None, data.split(FLAG)))
    decoded = []
    for frame in frames:
        current = remove_zeros(frame)

        # frame divided by gen has a reminder - frame is dysfunctional
        if get_div_rem(current) != '0' * (len(GEN) - 1):
            warn("Frame containing {} omitted.".format(frame))
        else:
            # cut the last len(gen) - 1 bits
            current = current[:-(len(GEN) - 1)]
            decoded.append(current)

    return "".join(decoded)


def create_files(source: str, target: str):
    # open Z.txt
    try:
        with open(source) as src:
            lines = src.read().splitlines()
    except FileNotFoundError:
        print("File not found.")
        return

    # read line after line from Z and encode
    coded_lines = [encode(line) + '\n' for line in lines]
    # write coded lines to file
    with open(target, 'w') as tgt:
        tgt.writelines(coded_lines)


def decode_files(source: str, target: str):
    try:
        with open(source) as src:
            lines = src.read().splitlines()
    except FileNotFoundError:
        print("File not found.")
        return

    coded_lines = [decode(line) + '\n' for line in lines]
    # write coded lines to file
    with open(target, 'w') as tgt:
        tgt.writelines(coded_lines)


if __name__ == '__main__':
    create_files("Z.txt", "W.txt")
    decode_files("W.txt", "G.txt")
