import math
import time

from Entities.FileBlock import FileBlock
from Entities.Inode import Inode
from commands.mount import mounted_partitions
from Entities.SuperBlock import SuperBlock


def mkfs(id_, fs):
    partition_dict = get_mounted_partition(id_)
    if partition_dict is None:
        print(f'Could not find mounted partition: {id_}')
        return
    if partition_dict['partition'].type == b'e':
        print('Cannot create file system in an extended partition')
        return

    super_block = SuperBlock()
    inode = Inode()
    fileblock = FileBlock()
    mounted_partition = partition_dict['partition']
    numerator = mounted_partition.size - super_block.getSuperBlockSize()
    denominator = 0
    if fs == '2fs':
        denominator = 4 + inode.getInodeSize() + 3 * fileblock.getFileBlockSize()
    else:
        denominator = -1
    n = math.floor(numerator / denominator)

    super_block.blocks_count = 0
    super_block.inodes_count = 0
    super_block.free_blocks_count = 3 * n
    super_block.free_inodes_count = n
    current_date = int(time.time())
    super_block.mtime = current_date
    super_block.umtime = current_date
    super_block.mcount = 1



def get_mounted_partition(id_):
    matching_partition = next((partition for partition in mounted_partitions if partition['id'] == id_),
                              None)

    if matching_partition is not None:
        return matching_partition
    else:
        return None
