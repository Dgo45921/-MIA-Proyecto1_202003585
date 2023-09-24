import ctypes
import struct

const = '<64s'


class FileBlock(ctypes.Structure):
    _fields_ = [
        ('b_content', ctypes.c_char * 64)
    ]

    def __init__(self):
        self.b_content = b'\x30' * 64

    def get_infomation(self):
        print("==Fileblock info")
        print(f"b_content: {self.b_content.decode()}")

    def getFileBlockSize(self):
        return struct.calcsize(const)

    def serialize(self):
        serialized = struct.pack(const, self.b_content)
        return serialized

    def deserialize(self, data):
        self.b_content = b'\x00\x00\x00\x00.\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x001,G,root\n1,U,root,root,123\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


def coding_str(string, size):
    return string.encode('utf-8')[:size].ljust(size, b'\0')
