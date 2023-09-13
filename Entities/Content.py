import ctypes
import struct


const = '<i 12s'


class Content(ctypes.Structure):
    _fields_ = [
        ("b_inodo", ctypes.c_int),
        ("b_name", ctypes.c_char * 12)
    ]

    def __init__(self):
        self.b_inodo = -1
        self.b_name = b'\0' * 12

    def get_infomation(self):
        print("==Content info")
        print(f"b_inodo: {self.b_inodo}")
        print(f"b_name: {self.b_name.decode()}")

    def getContentSize(self):
        return struct.calcsize(const)

    def serialize(self):
        serialize = struct.pack(
            const,
            self.b_inodo,
            self.b_name
        )
        return serialize

    def deserialize(self, data):
        self.b_inodo, self.b_name = struct.unpack(const, data)
