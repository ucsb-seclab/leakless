import itertools
import sys

verbose = False

def align(address, base, of):
    offset = (address - base) % of
    return address if offset == 0 else address + of - offset

def hex_bytes(string):
    return "".join(map(lambda x: chr(int(x, 16)), filter(len, string.split(" "))))

def findall(sub, string, addend):
    index = 0 - 1
    try:
        while True:
            index = string.index(sub, index + 1)
            yield index + addend
    except ValueError:
        pass

def find_all_strings(sections, string):
    result = [list(findall(string, section.data(), section.header.p_vaddr)) for section in sections if string in section.data()]
    return sum(result, [])

def find_string(sections, string):
    result = [section.header.p_vaddr + section.data().index(string) for section in sections if string in section.data()]
    return first_or_none(result)

def first_or_none(list):
    return list[0] if len(list) > 0 else None

def log(string):
    if verbose:
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

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def filter_none(list):
    return filter(lambda entry: entry is not None, list)

def insert_and_replace(original, insert, offset):
    return original[:offset] + insert + original[offset + len(insert):]
