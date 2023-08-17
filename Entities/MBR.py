import random
import time
import ctypes
import struct

pack_const = '<i i i'


class MBR(ctypes.Structure):
    _fields_ = [('size', ctypes.c_int),
                ('creationDate', ctypes.c_int),
                ('signature', ctypes.c_int)]

    def __init__(self):
        self.size = 0
        self.creationDate = int(time.time())
        self.signature = random.randint(0, 4294967295)

    def setSize(self, size):
        self.size = size

    def getSerializedMBR(self):
        serialized = struct.pack(
            pack_const,
            self.size,
            self.creationDate,
            self.signature
        )
        return serialized

    def deserialize(self, data):
        self.size, self.creationDate, self.signature = struct.unpack(pack_const, data)

    def printData(self):
        print('size: ', self.size, 'bytes')
        print('creation date: ', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.creationDate)))
        print('signature number: ', self.signature)

