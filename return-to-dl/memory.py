from utils import align, chunks

class Buffer:
    def __init__(self, exploit, start):
        self.start = start
        self.current = start
        self.areas = {}
        self.exploit = exploit
    def allocate(self, size, align_to=None, alignment=None, name=None):
        result = MemoryArea(self.exploit, self.current, size, align_to, alignment)
        self.current += result.size
        if name is not None:
            self.areas[name] = result
        return result

    def dump(self):
        result = ""
        for k, v in self.areas.iteritems():
            result += "Area " + k + "\n" + "\n".join([" " * 4 + line for line in v.dump().split("\n")]) + "\n"
        return result

class MemoryArea:
    def __init__(self, exploit, start, size, align_to=None, alignment=None):
        self.exploit = exploit
        if align_to is not None:
            if start < align_to:
                raise Exception("Trying to align to a something which is after our buffer: aligning " + self.exploit.pointer_format % start + " to " + self.exploit.pointer_format % align_to)
            self.align_to = align_to
            self.alignment = size if (alignment is None) else alignment
            self.start = align(start, self.align_to, self.alignment)
            self.index = (self.start - self.align_to) / self.alignment
        else:
            self.alignment = 1
            self.align_to = 0
            self.start = start
            self.index = 0

        self.content = ""
        self.pointer = self.exploit.ptr2str(self.start)
        self.size = size
        self.end = self.start + self.size

    def dump(self):
        result = ""
        result += "Start: " + self.exploit.pointer_format % self.start + "\n"
        result += "Size: " + self.exploit.pointer_format % self.size + " (" + str(self.size) + ")\n"
        result += "End: " + self.exploit.pointer_format % self.end + "\n"
        result += "Base: " + self.exploit.pointer_format % self.align_to + "\n"
        result += "Alignment: " + str(self.alignment) + "\n"
        result += "Index: " + hex(self.index) + " (" + str(self.index) + ")\n"
        result += "Content:\n"
        for chunk in chunks(self.content, self.exploit.pointer_size):
            result += " " * 4 + " ".join(["%.2x" % ord(c) for c in chunk]) + " " + self.exploit.pointer_format % self.exploit.str2ptr(chunk) + "\n"
        return result
