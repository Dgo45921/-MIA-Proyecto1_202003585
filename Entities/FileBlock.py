import ctypes
import struct

const = '<64s'


class FileBlock(ctypes.Structure):
    _fields_ = [
        ('b_content', ctypes.c_char * 64),
    ]

    def __init__(self):
        self.b_content = b'\0' * 64

    def set_infomation(self, b_content):
        self.b_content = coding_str(b_content, 64)

    def get_infomation(self):
        print("==Fileblock info")
        print(f"b_content: {self.b_content.decode()}")

    def getFileBlockSize(self):
        return struct.calcsize(const)

    def serialize(self):
        serialize = struct.pack(
            const,
            self.b_content,
        )
        return serialize

    def doDeserialize(self, data):
        self.b_content = struct.unpack(const, data)


def coding_str(string, size):
    return string.encode('utf-8')[:size].ljust(size, b'\0')
