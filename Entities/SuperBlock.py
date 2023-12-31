import ctypes
import struct

pack_const = '<i i i i i i i i H i i i i i i i i'


class SuperBlock(ctypes.Structure):
    _fields_ = [
        ('filesystem_type', ctypes.c_int),
        ('inodes_count', ctypes.c_int),
        ('blocks_count', ctypes.c_int),
        ('free_blocks_count', ctypes.c_int),
        ('free_inodes_count', ctypes.c_int),
        ('mtime', ctypes.c_int),
        ('umtime', ctypes.c_int),
        ('mcount', ctypes.c_int),
        ('magic', ctypes.c_uint16),
        ('inode_size', ctypes.c_int),
        ('block_size', ctypes.c_int),
        ('first_ino', ctypes.c_int),
        ('first_blo', ctypes.c_int),
        ('bm_inode_start', ctypes.c_int),
        ('bm_block_start', ctypes.c_int),
        ('inode_start', ctypes.c_int),
        ('block_start', ctypes.c_int),
    ]

    def __init__(self):
        self.magic = 0xEF53

    def get_infomation(self):
        print("Superblock info")
        print(f"filesystem_type: {self.filesystem_type}")
        print(f"inodes_count: {self.inodes_count}")
        print(f"blocks_count: {self.blocks_count}")
        print(f"free_blocks_count: {self.free_blocks_count}")
        print(f"free_inodes_count: {self.free_inodes_count}")
        print(f"mtime: {self.mtime}")
        print(f"umtime: {self.umtime}")
        print(f"mcount: {self.mcount}")
        print(f"magic: {hex(self.magic)}")
        print(f"inode_size: {self.inode_size}")
        print(f"block_size: {self.block_size}")
        print(f"first_ino: {self.first_ino}")
        print(f"first_blo: {self.first_blo}")
        print(f"bm_inode_start: {self.bm_inode_start}")
        print(f"bm_block_start: {self.bm_block_start}")
        print(f"inode_start: {self.inode_start}")
        print(f"block_start: {self.block_start}")

    def getSuperBlockSize(self):
        return struct.calcsize(pack_const)

    def deserialize(self, data):
        (self.filesystem_type,
         self.inodes_count,
         self.blocks_count,
         self.free_blocks_count,
         self.free_inodes_count,
         self.mtime,
         self.umtime,
         self.mcount,
         self.magic,
         self.inode_size,
         self.block_size,
         self.first_ino,
         self.first_blo,
         self.bm_inode_start,
         self.bm_block_start,
         self.inode_start,
         self.block_start) = struct.unpack(pack_const, data)

    def serialize(self):
        serialize = struct.pack(
            pack_const,
            self.filesystem_type,
            self.inodes_count,
            self.blocks_count,
            self.free_blocks_count,
            self.free_inodes_count,
            self.mtime,
            self.umtime,
            self.mcount,
            self.magic,
            self.inode_size,
            self.block_size,
            self.first_ino,
            self.first_blo,
            self.bm_inode_start,
            self.bm_block_start,
            self.inode_start,
            self.block_start,
        )
        return serialize
