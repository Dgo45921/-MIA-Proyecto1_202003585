import random
import time
import ctypes
import struct

from Entities.Partition import Partition

pack_const = '< i i i 1s'


class MBR(ctypes.Structure):
    _fields_ = [('size', ctypes.c_int),
                ('creationDate', ctypes.c_int),
                ('signature', ctypes.c_int),
                ('fit', ctypes.c_char * 1)
                ]

    def __init__(self):
        self.size = 0
        self.creationDate = int(time.time())
        self.signature = random.randint(0, 4294967295)
        self.fit = b'\x46'
        self.partition1 = Partition()
        self.partition2 = Partition()
        self.partition3 = Partition()
        self.partition4 = Partition()

    def setAttributes(self, size, fit):
        self.size = size
        self.fit = bytes(fit, 'ascii')

    def getSerializedMBR(self):
        serialized_partition = self.partition1.getSerializedPartition()
        serialized = struct.pack(
            pack_const,
            self.size,
            self.creationDate,
            self.signature,
            self.fit
        )
        return serialized + serialized_partition * 4

    def deserialize(self, data):
        mbr_size = self.getMBRSize()
        partition_size = self.partition1.getSerializedPartitionSize()
        # de serializing basic parameters of mbr
        mbr_data = data[:mbr_size]
        self.size, self.creationDate, self.signature, self.fit = struct.unpack(pack_const, mbr_data)
        # de serializing partition 1 data

        partition1_data = data[mbr_size:mbr_size + partition_size]
        self.partition1 = Partition()
        self.partition1.deserialize(partition1_data)
        # de serializing partition 2 data

        partition2_data = data[mbr_size + partition_size:mbr_size + partition_size * 2]
        self.partition2 = Partition()
        self.partition2.deserialize(partition2_data)

        # de serializing partition 3 data

        partition3_data = data[mbr_size + partition_size * 2:mbr_size + partition_size * 3]
        self.partition3 = Partition()
        self.partition3.deserialize(partition3_data)

        # de serializing partition 4 data

        partition4_data = data[mbr_size + partition_size * 3:mbr_size + partition_size * 4]
        self.partition4 = Partition()
        self.partition4.deserialize(partition4_data)

    def printData(self):
        print('size: ', self.size, 'bytes')
        print('creation date: ', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.creationDate)))
        print('signature number: ', self.signature)
        print('fit: ', self.fit.decode('utf-8'))

        print('-------PARTITION 1--------')
        self.partition1.printPartitionData()
        print('-------PARTITION 2--------')
        self.partition2.printPartitionData()
        print('-------PARTITION 3--------')
        self.partition3.printPartitionData()
        print('-------PARTITION 4--------')
        self.partition4.printPartitionData()



    def getMBRSize(self):
        return struct.calcsize(pack_const)
