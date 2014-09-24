import sys

def align(address, base, of):
    offset = (address - base) % of
    return address if offset == 0 else address + of - offset

def hex_bytes(string):
    return "".join(map(lambda x: chr(int(x, 16)), filter(len, string.split(" "))))

def find_string(sections, string):
    result = [section.header.p_vaddr + section.data().index(string) for section in sections if string in section.data()]
    return first_or_none(result)

def first_or_none(list):
    return list[0] if len(list) > 0 else None

def log(string):
    sys.stderr.write(string + "\n")

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def integer_to_bigendian(n):
    s = '%x' % n
    if len(s) & 1:
        s = '0' + s
    return s.decode('hex')

def bigendian_to_integer(string):
    return string.encode("hex")
