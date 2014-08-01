import os
import sys
import select
from time import time

#
# Helper functions
# 

debug_level = 3 # Higher values, higher importance
address_bits = 32 # Not all functions use this, don't rely on it yet

address_string_len = (address_bits / 8) * 2

# Don't buffer stdout and stderr
class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

def unbuffer_streams():
    sys.stdout = Unbuffered(sys.stdout)
    sys.stderr = Unbuffered(sys.stderr)


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

# TODO: some of these functions are not really using address_string_len
def hex2le(addr, padding=address_string_len):
    if (not addr) or len(addr) == 0:
        addr = ""
    addr = addr.replace(" ", "")
    if len(addr) < padding:
        addr = "0" * int(padding - len(addr))
    return bytearray([chr(int(x, 16)) for x in reversed(list(chunks(addr, 2)))])

clean_hex = lambda inte: hex(inte).replace("0x", "").replace("L", "")
lepad = lambda chars: pad(chars, 4, b'\x00', False)
le2hex = lambda chars: "".join([("0" if x < 16 else "") + \
                                clean_hex(bytearray(x)[0]) for x in list(reversed(lepad(chars)))])

le2hex = lambda chars: "".join([pad(clean_hex(x), 2) for x in bytearray(list(reversed(lepad(chars))))])

le2int = lambda chars: int(le2hex(chars), 16)
int2hex = lambda inte: ("0" * int(address_string_len - len(clean_hex(inte)))) + \
                       clean_hex(inte)
int2le = lambda inte: hex2le(int2hex(inte))

# TODO: make this configurable
int2bytes = int2le
bytes2int = le2int
bytes2hex = le2hex
hex2bytes = hex2le

def pad(string, length, char='0', left=True):
    if (not string) or len(string) == 0:
        string = ""
    pad_str = char * int(length - len(string))
    return (pad_str + string) if left else (string + pad_str)

pad_left = pad
pad_right = lambda string, length, char: pad(string, length, char, False)

def log(string, level=3):
    if level >= debug_level:
        sys.stderr.write("[" + str(level) + ":" + \
          "{:18.6f}".format(time()).replace(" ", "0") + "] " + string + "\n")

def write_bytes(bytes):
    os.write(sys.stdout.fileno(), bytes)

def read_bytes(length):
    return os.read(sys.stdin.fileno(), length)

def write_string(string):
    sys.stdout.write(string)

def read_string(length):
    return sys.stdin.read(length)

# def read_all():
#     return sys.stdin.read()

def read_all(p):
    buf = ""
    read = ""
    while True:
        ready, _, _ = select.select((p,), (), (), .1)
        if p in ready:
            read = p.read(1)
            if len(read) == 0:
               return buf
            else:
               buf += read
        else:
            return buf
    return buf
