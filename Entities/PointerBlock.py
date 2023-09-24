import struct


def code_str(string, size):
    return string.encode('utf-8')[:size].ljust(size, b'\0')


pack_const = "<16i"


class PointerBlock:
    def __init__(self):
        self.b_pointers = [-1] * 16

    def setB_pointers(self, b_pointers):
        self.b_pointers = b_pointers

    def deserialize(self, data):
        self.b_pointers = struct.unpack(pack_const, data)

    def serialize(self):
        res = struct.pack(pack_const, *self.b_pointers)
        return res

    def getBlockSize(self):
        return struct.calcsize(pack_const)

