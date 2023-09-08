import ctypes
import struct

pack_const = '< 1s 1s i i i 16s'

# 30 bytes


class EBR(ctypes.Structure):
    _fields_ = [('status', ctypes.c_char),
                ('fit', ctypes.c_char),
                ('start', ctypes.c_int),
                ('size', ctypes.c_int),
                ('next', ctypes.c_int),
                ('name', ctypes.c_char * 16)
                ]

    def __init__(self):
        self.status = b'0'
        self.fit = b'f'
        self.start = -1
        self.size = 0
        self.next = -1
        self.name = b'\x30' * 16

    def setAttributes(self, size, fit):
        self.size = size
        self.fit = bytes(fit, 'ascii')

    def getSerializedEBR(self):
        serialized = struct.pack(
            pack_const,
            self.status,
            self.fit,
            self.start,
            self.size,
            self.next,
            self.name
        )
        return serialized

    def deserialize(self, data):

        self.status, self.fit, self.start, self.size, self.next, self.name = struct.unpack(pack_const, data)


    def printData(self):
        print('size: ', self.size, 'bytes')
        print('fit: ', self.fit.decode('utf-8'))

    def getEBRsize(self):
        return struct.calcsize(pack_const)
