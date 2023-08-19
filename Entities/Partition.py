import ctypes
import struct

pack_const = '< 1s 1s 1s i i 16s'


class Partition(ctypes.Structure):
    _fields_ = [('status', ctypes.c_char * 1),
                ('type', ctypes.c_char * 1),
                ('fit', ctypes.c_char * 1),
                ('start', ctypes.c_int),
                ('size', ctypes.c_int),
                ('name', ctypes.c_char * 16)
                ]

    def __init__(self):
        self.status = b'\x30'  # byte '0' = inactivo, 1 = activo
        self.type = b'\x00'
        self.fit = b'\x00'
        self.start = -1
        self.size = 0
        self.name = b'\x00' * 16

    def getSerializedPartition(self):
        serialized = struct.pack(
            pack_const,
            self.status,
            self.type,
            self.fit,
            self.start,
            self.size,
            self.name
        )
        return serialized

    def getSerializedPartitionSize(self):
        return struct.calcsize(pack_const)

    def deserialize(self, data):
        self.status, self.type, self.fit, self.start, self.size, self.name = struct.unpack(pack_const, data)

    def printPartitionData(self):
        print('Status: ', self.status)
        print('Type: ', self.type)
        print('Fit: ', self.fit)
        print('Start: ', self.start)
        print('Size: ', self.size)
        print('Name: ', self.name)

    def equalToDefault(self, partition):
        return (partition.status == self.status and partition.type == self.type and partition.fit == self.fit and
                partition.start == self.start and partition.size == self.size and partition.name == self.name)

    def makeDefault(self):
        self = Partition()

