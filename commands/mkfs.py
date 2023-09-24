import math
import time

from Entities.EBR import EBR
from Entities.FileBlock import FileBlock, coding_str
from Entities.FolderBlock import Folderblock
from Entities.Inode import Inode
from commands.mount import mounted_partitions
from Entities.SuperBlock import SuperBlock


def mkfs(id_, fs):
    partition_dict = get_mounted_partition(id_)
    if partition_dict is None:
        print(f'Could not find mounted partition: {id_}')
        return
    if not isinstance(partition_dict['partition'], EBR):
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
    if fs == '2fs':
        createEXT2(n, partition_dict['partition'], super_block, partition_dict['disk_path'])


def createEXT2(n, found_partition, new_super_block, path):
    new_super_block.filesystem_type = 2
    if isinstance(found_partition, EBR):
        new_super_block.bm_inode_start = found_partition.start + found_partition.getEBRsize() + new_super_block.getSuperBlockSize()
        new_super_block.bm_block_start = new_super_block.bm_inode_start + n
        new_super_block.inode_start = new_super_block.bm_block_start + 3 * n
        new_super_block.block_start = new_super_block.inode_start + n * Inode().getInodeSize()

        # creating user file
        new_super_block.free_inodes_count -= 1
        new_super_block.free_blocks_count -= 1
        new_super_block.free_inodes_count -= 1
        new_super_block.free_blocks_count -= 1

        new_super_block.inodes_count = n
        new_super_block.blocks_count = 3 * n

        zero = b'\x00'
        disk_file = open(path, 'rb+')
        for i in range(n):
            disk_file.seek(new_super_block.bm_inode_start + i)
            disk_file.write(zero)

        for i in range(3 * n):
            disk_file.seek(new_super_block.bm_block_start + i)
            disk_file.write(zero)

        new_Inode = Inode()
        for i in range(n):
            disk_file.seek(new_super_block.inode_start + i * new_Inode.getInodeSize())
            disk_file.write(new_Inode.serialize())

        new_file_block = FileBlock()
        for i in range(n):
            disk_file.seek(new_super_block.block_start + i * new_file_block.getFileBlockSize())
            disk_file.write(new_file_block.serialize())

        current_date = int(time.time())

        # root folder inode

        Inode0 = Inode()
        Inode0.i_uid = 1
        Inode0.i_gid = 1
        Inode0.i_size = 0
        Inode0.i_atime = current_date
        Inode0.i_ctime = current_date
        Inode0.i_mtime = current_date
        Inode0.i_type = b'0'  # this is a  folder inode
        Inode0.i_perm = b'664'
        Inode0.i_block[0] = 0

        # block for the root folder
        Folderblock0 = Folderblock()
        Folderblock0.Content[0].b_inodo = 0
        Folderblock0.Content[0].b_name = b'.'
        Folderblock0.Content[1].b_inodo = 0
        Folderblock0.Content[1].b_name = b'..'
        Folderblock0.Content[2].b_inodo = 1
        Folderblock0.Content[2].b_name = b'user.txt'

        # inode for the user file
        Inode1 = Inode()
        Inode1.i_uid = 1
        Inode1.i_gid = 1
        Inode1.i_size = new_file_block.getFileBlockSize()
        Inode1.i_atime = current_date
        Inode1.i_ctime = current_date
        Inode1.i_mtime = current_date
        Inode1.i_type = b'1'
        Inode1.i_perm = b'664'
        Inode1.i_block[0] = 1

        data_usertxt = '1,G,root\n1,U,root,root,123\n'
        Fileblock1 = FileBlock()
        Fileblock1.b_content = coding_str(data_usertxt, 64)

        new_super_block.first_blo = 2
        new_super_block.first_ino = 2

        new_super_block.inode_size = Inode1.getInodeSize()
        new_super_block.block_size = Fileblock1.getFileBlockSize()

        # writing super block
        disk_file.seek(found_partition.start + found_partition.getEBRsize())
        disk_file.write(new_super_block.serialize())

        # updating the bitmap of inodes
        disk_file.seek(new_super_block.bm_inode_start)
        disk_file.write(b'\1')
        disk_file.seek(new_super_block.bm_inode_start + 1)
        disk_file.write(b'\1')

        # updating bitmap of blocks
        disk_file.seek(new_super_block.bm_block_start)
        disk_file.write(b'\1')
        disk_file.seek(new_super_block.bm_block_start + 1)
        disk_file.write(b'\1')

        # writing created folder and file inodes
        disk_file.seek(new_super_block.inode_start)
        disk_file.write(Inode0.serialize())
        disk_file.seek(new_super_block.inode_start + Inode1.getInodeSize())
        disk_file.write(Inode1.serialize())

        # fill blocks

        disk_file.seek(new_super_block.block_start)
        disk_file.write(Folderblock0.serialize())
        disk_file.seek(new_super_block.block_start + Folderblock0.getFolderBlockSize())
        disk_file.write(Fileblock1.serialize())

        disk_file.close()

        print('EXT2 format done!')
    else:
        new_super_block.bm_inode_start = found_partition.start + new_super_block.getSuperBlockSize()
        new_super_block.bm_block_start = new_super_block.bm_inode_start + n
        new_super_block.inode_start = new_super_block.bm_block_start + 3 * n
        new_super_block.block_start = new_super_block.inode_start + n * Inode().getInodeSize()

        # creating user file
        new_super_block.free_inodes_count -= 1
        new_super_block.free_blocks_count -= 1
        new_super_block.free_inodes_count -= 1
        new_super_block.free_blocks_count -= 1

        new_super_block.inodes_count = n
        new_super_block.blocks_count = 3 * n

        zero = b'\x00'
        disk_file = open(path, 'rb+')
        for i in range(n):
            disk_file.seek(new_super_block.bm_inode_start + i)
            disk_file.write(zero)

        for i in range(3 * n):
            disk_file.seek(new_super_block.bm_block_start + i)
            disk_file.write(zero)

        new_Inode = Inode()
        for i in range(n):
            disk_file.seek(new_super_block.inode_start + i * new_Inode.getInodeSize())
            disk_file.write(new_Inode.serialize())

        new_file_block = FileBlock()
        for i in range(n):
            disk_file.seek(new_super_block.block_start + i * new_file_block.getFileBlockSize())
            disk_file.write(new_file_block.serialize())

        current_date = int(time.time())

        # root folder inode

        Inode0 = Inode()
        Inode0.i_uid = 1
        Inode0.i_gid = 1
        Inode0.i_size = 0
        Inode0.i_atime = current_date
        Inode0.i_ctime = current_date
        Inode0.i_mtime = current_date
        Inode0.i_type = b'0'  # this is a  folder inode
        Inode0.i_perm = b'664'
        Inode0.i_block[0] = 0

        # block for the root folder
        Folderblock0 = Folderblock()
        Folderblock0.Content[0].b_inodo = 0
        Folderblock0.Content[0].b_name = b'.'
        Folderblock0.Content[1].b_inodo = 0
        Folderblock0.Content[1].b_name = b'..'
        Folderblock0.Content[2].b_inodo = 1
        Folderblock0.Content[2].b_name = b'user.txt'

        # inode for the user file
        Inode1 = Inode()
        Inode1.i_uid = 1
        Inode1.i_gid = 1
        Inode1.i_size = new_file_block.getFileBlockSize()
        Inode1.i_atime = current_date
        Inode1.i_ctime = current_date
        Inode1.i_mtime = current_date
        Inode1.i_type = b'1'
        Inode1.i_perm = b'664'
        Inode1.i_block[0] = 1

        data_usertxt = '1,G,root\n1,U,root,root,123\n'
        Fileblock1 = FileBlock()
        Fileblock1.b_content = coding_str(data_usertxt, 64)

        new_super_block.first_blo = 2
        new_super_block.first_ino = 2

        new_super_block.inode_size = Inode1.getInodeSize()
        new_super_block.block_size = Fileblock1.getFileBlockSize()

        # writing super block
        disk_file.seek(found_partition.start)
        disk_file.write(new_super_block.serialize())

        # updating the bitmap of inodes
        disk_file.seek(new_super_block.bm_inode_start)
        disk_file.write(b'\1')
        disk_file.seek(new_super_block.bm_inode_start + 1)
        disk_file.write(b'\1')

        # updating bitmap of blocks
        disk_file.seek(new_super_block.bm_block_start)
        disk_file.write(b'\1')
        disk_file.seek(new_super_block.bm_block_start + 1)
        disk_file.write(b'\1')

        # writing created folder and file inodes
        disk_file.seek(new_super_block.inode_start)
        disk_file.write(Inode0.serialize())
        disk_file.seek(new_super_block.inode_start + Inode1.getInodeSize())
        disk_file.write(Inode1.serialize())

        # fill blocks

        disk_file.seek(new_super_block.block_start)
        disk_file.write(Folderblock0.serialize())
        disk_file.seek(new_super_block.block_start + Folderblock0.getFolderBlockSize())
        disk_file.write(Fileblock1.serialize())

        disk_file.close()

        print('EXT2 format done!')




def get_mounted_partition(id_):
    matching_partition = next((partition for partition in mounted_partitions if partition['id'] == id_),
                              None)

    if matching_partition is not None:
        return matching_partition
    else:
        return None
