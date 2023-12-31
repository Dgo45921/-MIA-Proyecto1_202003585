import html
import os
import time
from itertools import chain

from Entities.EBR import EBR
from Entities.FileBlock import FileBlock
from Entities.FolderBlock import Folderblock
from Entities.Inode import Inode
from Entities.MBR import MBR
from Entities.PointerBlock import PointerBlock
from Entities.SuperBlock import SuperBlock
from utils.graphviz import basicMBR_report
from commands.mount import get_mounted_partition


def repCommand(args):
    try:
        file_path = args.path
        newmbr = MBR()
        with open(file_path, 'rb') as file:
            file.seek(0)
            data = file.read(newmbr.getMBRSize() + newmbr.partition1.getSerializedPartitionSize() * 4)
            # print("Size data: ",  len(data))
            newmbr.deserialize(data)
            file.close()
        newmbr.printData()

        # TODO CREATE GRAPHVIZ OF PARTITIONS
        basicMBR_report(newmbr, args)

    except Exception as e:
        print("An error occurred:", e)


def rep_mbr(id_, output_path):
    if " " in output_path:
        '"' + output_path + '"'

    if not (output_path.endswith(".jpg") or output_path.endswith(".png") or output_path.endswith('.pdf')):
        print('Error, output extension must be .jpg, .png or .pdf')

    mounted_partition = get_mounted_partition(id_)
    if mounted_partition is None:
        print(f'Error, no mounted partition {id_}')
        return

    found_mbr = MBR()
    with open(mounted_partition['disk_path'], 'rb') as file:
        file.seek(0)
        data = file.read(found_mbr.getMBRSize() + found_mbr.partition1.getSerializedPartitionSize() * 4)
        found_mbr.deserialize(data)
        file.close()

    partitions = [found_mbr.partition1, found_mbr.partition2, found_mbr.partition3, found_mbr.partition4]
    code = get_mbr_viz_code(found_mbr, partitions, mounted_partition['disk_path'])

    directory = os.path.dirname(output_path)
    os.makedirs(directory, exist_ok=True)
    file_name = os.path.basename(output_path)

    with open(directory + "/" + file_name.split('.')[0] + '.dot', 'w') as f:
        f.write(code)
        f.close()

    if file_name.endswith('.jpg'):
        os.system(
            "dot -Tjpg \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')
    elif file_name.endswith('.png'):
        os.system(
            "dot -Tpng \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')
    elif file_name.endswith('.pdf'):
        os.system(
            "dot -Tpdf \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')

    print(f'mbr report generated in {directory}')


def rep_disk(id_, output_path):
    if " " in output_path:
        '"' + output_path + '"'

    if not (output_path.endswith(".jpg") or output_path.endswith(".png") or output_path.endswith('.pdf')):
        print('Error, output extension must be .jpg, .png or .pdf')

    mounted_partition = get_mounted_partition(id_)
    if mounted_partition is None:
        print(f'Error, no mounted partition {id_}')
        return

    found_mbr = MBR()
    with open(mounted_partition['disk_path'], 'rb') as file:
        file.seek(0)
        data = file.read(found_mbr.getMBRSize() + found_mbr.partition1.getSerializedPartitionSize() * 4)
        found_mbr.deserialize(data)
        file.close()

    partitions_spaces = [
        {'size': found_mbr.size, 'start_byte': 0},
        {'size': found_mbr.partition1.size, 'start_byte': found_mbr.partition1.start},
        {'size': found_mbr.partition2.size, 'start_byte': found_mbr.partition2.start},
        {'size': found_mbr.partition3.size, 'start_byte': found_mbr.partition3.start},
        {'size': found_mbr.partition4.size, 'start_byte': found_mbr.partition4.start}
    ]

    partitions = [found_mbr.partition1, found_mbr.partition2, found_mbr.partition3, found_mbr.partition4]

    directory = os.path.dirname(output_path)
    os.makedirs(directory, exist_ok=True)
    file_name = os.path.basename(output_path)

    blank_spaces = find_empty_spaces(found_mbr.size, partitions_spaces)
    partitions_spaces.pop(0)
    code = get_disk_viz_code(found_mbr, partitions_spaces, blank_spaces, partitions, mounted_partition['disk_path'])
    with open(directory + "/" + file_name.split('.')[0] + '.dot', 'w') as f:
        f.write(code)
        f.close()

    if file_name.endswith('.jpg'):
        os.system(
            "dot -Tjpg \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')
    elif file_name.endswith('.png'):
        os.system(
            "dot -Tpng \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')
    elif file_name.endswith('.pdf'):
        os.system(
            "dot -Tpdf\"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')

    print(f'disk report generated in {directory}')


def rep_inode(id_, output_path):
    if " " in output_path:
        '"' + output_path + '"'

    if not (output_path.endswith(".jpg") or output_path.endswith(".png") or output_path.endswith('.pdf')):
        print('Error, output extension must be .jpg, .png or .pdf')
        return

    partition_dict = get_mounted_partition(id_)
    if partition_dict is None:
        print(f'Error, no mounted partition {id_}')
        return

    mounted_partition = partition_dict['partition']

    if mounted_partition.type == b'e':
        print('Cannot get superblock report for an extended partition!')
        return

    super_block = SuperBlock()
    disk_file = open(partition_dict['disk_path'], 'rb+')
    disk_file.seek(mounted_partition.start)
    sb_data = disk_file.read(super_block.getSuperBlockSize())
    super_block.deserialize(sb_data)
    disk_file.close()

    code = get_dot_inode(super_block, partition_dict['disk_path'])

    directory = os.path.dirname(output_path)
    os.makedirs(directory, exist_ok=True)
    file_name = os.path.basename(output_path)

    with open(directory + "/" + file_name.split('.')[0] + '.dot', 'w') as f:
        f.write(code)
        f.close()

    if file_name.endswith('.jpg'):
        os.system(
            "dot -Tjpg \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')
    elif file_name.endswith('.png'):
        os.system(
            "dot -Tpng \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')
    elif file_name.endswith('.pdf'):
        os.system(
            "dot -Tpdf \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')

    print(f'inode report generated in {directory}')


def rep_block(id_, output_path):
    if " " in output_path:
        '"' + output_path + '"'

    if not (output_path.endswith(".jpg") or output_path.endswith(".png") or output_path.endswith('.pdf')):
        print('Error, output extension must be .jpg, .png or .pdf')
        return

    partition_dict = get_mounted_partition(id_)
    if partition_dict is None:
        print(f'Error, no mounted partition {id_}')
        return

    mounted_partition = partition_dict['partition']

    if mounted_partition.type == b'e':
        print('Cannot get superblock report for an extended partition!')
        return

    super_block = SuperBlock()
    disk_file = open(partition_dict['disk_path'], 'rb+')
    disk_file.seek(mounted_partition.start)
    sb_data = disk_file.read(super_block.getSuperBlockSize())
    super_block.deserialize(sb_data)
    disk_file.close()

    code = get_dot_block(super_block, partition_dict['disk_path'])

    directory = os.path.dirname(output_path)
    os.makedirs(directory, exist_ok=True)
    file_name = os.path.basename(output_path)

    with open(directory + "/" + file_name.split('.')[0] + '.dot', 'w') as f:
        f.write(code)
        f.close()

    if file_name.endswith('.jpg'):
        os.system(
            "dot -Tjpg \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')
    elif file_name.endswith('.png'):
        os.system(
            "dot -Tpng \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')
    elif file_name.endswith('.pdf'):
        os.system(
            "dot -Tpdf \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')

    print(f'block report generated in {directory}')


def get_dot_inode(super_block, file_path):
    dot_code = """digraph G {
        node [shape=box];
        """

    disk_file = open(file_path, 'rb+')

    bitmap = []

    for i in range(super_block.inodes_count):
        disk_file.seek(super_block.bm_inode_start + i)
        bitmap.append(disk_file.read(1))

    for i in range(super_block.inodes_count):
        if bitmap[i] == b'\x00':
            continue
        inode = Inode()
        disk_file.seek(super_block.inode_start + i * inode.getInodeSize())
        inode.deserialize(disk_file.read(inode.getInodeSize()))

        if inode.i_type == b'0':
            dot_code += (
                f'node{i} [label="i_uid: {inode.i_uid} &#92;n i_gid: {inode.i_gid} &#92;n i_size: {inode.i_size} &#92;n i_atime: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(inode.i_atime))} '
                f'&#92;n i_ctime: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(inode.i_ctime))} &#92;n i_mtime: '
                f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(inode.i_mtime))} &#92;n i_block: {" ".join(map(str, inode.i_block))} &#92;n'
                f'i_type: Carpeta   &#92;n i_perm: {inode.i_perm} "];\n')

        else:
            dot_code += (
                f'node{i} [label="i_uid: {inode.i_uid} &#92;n i_gid: {inode.i_gid} &#92;n i_size: {inode.i_size} &#92;n i_atime: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(inode.i_atime))} '
                f'&#92;n i_ctime: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(inode.i_ctime))} &#92;n i_mtime: '
                f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(inode.i_mtime))} &#92;n i_block: {" ".join(map(str, inode.i_block))} &#92;n'
                f'i_type: Archivo   &#92;n i_perm: {inode.i_perm} "];\n')

    dot_code += '}'

    disk_file.close()
    return dot_code


def get_dot_block(super_block, file_path):
    dot_code = """digraph G {
        node [shape=box];
        """

    disk_file = open(file_path, 'rb+')

    bitmap = []

    for i in range(super_block.blocks_count):
        disk_file.seek(super_block.bm_block_start + i)
        bitmap.append(disk_file.read(1))

    for i in range(super_block.blocks_count):
        if bitmap[i] == b'\x00':
            continue
        lol = PointerBlock()
        disk_file.seek(super_block.block_start + i * lol.getBlockSize())
        lol.deserialize(disk_file.read(lol.getBlockSize()))
        imprimir = True

        for x in lol.b_pointers:
            if x > super_block.blocks_count or x == 0:
                imprimir = False
                break

        if imprimir:
            dot_code += f'node{i} [label="i_uid: {" ".join(map(str, lol.b_pointers))}]'
            continue

        if not imprimir:
            imprimir = True
            ignore = [".", ".."]
            lol = Folderblock()
            disk_file.seek(super_block.block_start + i * lol.getFolderBlockSize())
            lol.deserialize(disk_file.read(lol.getFolderBlockSize2()))
            for x in lol.Content:
                if x.b_inodo > super_block.inodes_count or (
                        x.b_inodo == 0 and x.b_name.decode().strip("\x00") not in ignore):
                    imprimir = False
                    break

        if imprimir:
            for content in lol.Content:
                dot_code += (
                    f'node{i} [label="b_inodo: {content.b_inodo} &#92;n b_name: {content.b_name.decode("utf-8")}]')
            continue

        if not imprimir:
            lol = FileBlock()
            disk_file.seek(super_block.block_start + i * lol.getFileBlockSize())
            lol.deserialize(disk_file.read(lol.getFileBlockSize()))
            dot_code += f'node{i} [label="b_content: {html.escape(lol.b_content.decode("utf-8"))}"]\n'
            continue

    dot_code += '}'

    disk_file.close()
    return dot_code


def rep_bm(id_, output_path, bm_type):
    if " " in output_path:
        '"' + output_path + '"'

    if not (output_path.endswith('.txt')):
        print('Error, output extension must be .txt')
        return

    partition_dict = get_mounted_partition(id_)
    if partition_dict is None:
        print(f'Error, no mounted partition {id_}')
        return

    mounted_partition = partition_dict['partition']

    if mounted_partition.type == b'e':
        print('Cannot get superblock report for an extended partition!')
        return

    super_block = SuperBlock()
    disk_file = open(partition_dict['disk_path'], 'rb+')
    disk_file.seek(mounted_partition.start)
    sb_data = disk_file.read(super_block.getSuperBlockSize())
    super_block.deserialize(sb_data)

    text = ""

    if bm_type == 1:
        counter = 0
        for i in range(super_block.inodes_count):
            disk_file.seek(super_block.bm_inode_start + i)
            if counter == 20:
                text += '\n'
                counter = 0

            val = disk_file.read(1)
            if val == b'\1':
                text += '1'
            else:
                text += '0'
            counter += 1
    else:
        counter = 0
        for i in range(super_block.blocks_count):
            disk_file.seek(super_block.bm_block_start + i)
            if counter == 20:
                text += '\n'
                counter = 0

            val = disk_file.read(1)
            if val == b'\1':
                text += '1'
            else:
                text += '0'
            counter += 1

    disk_file.close()
    directory = os.path.dirname(output_path)
    os.makedirs(directory, exist_ok=True)
    file_name = os.path.basename(output_path)

    with open(directory + "/" + file_name.split('.')[0] + '.txt', 'w') as f:
        f.write(text)
        f.close()

    print(f'Bitmap report generated in: {output_path}')


def rep_sb(id_, output_path):
    if " " in output_path:
        '"' + output_path + '"'

    if not (output_path.endswith(".jpg") or output_path.endswith(".png") or output_path.endswith('.pdf')):
        print('Error, output extension must be .jpg, .png or .pdf')

    partition_dict = get_mounted_partition(id_)
    if partition_dict is None:
        print(f'Error, no mounted partition {id_}')
        return

    mounted_partition = partition_dict['partition']

    if not isinstance(mounted_partition, EBR):
        if mounted_partition.type == b'e':
            print('Cannot get superblock report for an extended partition!')
            return

    super_block = SuperBlock()
    disk_file = open(partition_dict['disk_path'], 'rb+')
    disk_file.seek(mounted_partition.start)
    sb_data = disk_file.read(super_block.getSuperBlockSize())
    super_block.deserialize(sb_data)
    disk_file.close()

    code = get_sb_viz_code(super_block, partition_dict['disk_path'])
    directory = os.path.dirname(output_path)
    os.makedirs(directory, exist_ok=True)
    file_name = os.path.basename(output_path)

    with open(directory + "/" + file_name.split('.')[0] + '.dot', 'w') as f:
        f.write(code)
        f.close()

    if file_name.endswith('.jpg'):
        os.system(
            "dot -Tjpg \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')
    elif file_name.endswith('.png'):
        os.system(
            "dot -Tpng \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')
    elif file_name.endswith('.pdf'):
        os.system(
            "dot -Tpdf\"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"' + output_path + '"')

    print(f'superblock report generated in: {directory}')


def get_sb_viz_code(sb, disk_name):
    vizcode = """digraph G {
    node [shape=plaintext];
    
    struct [label=<<table border="1" cellborder="1" cellspacing="0">
        <tr><td bgcolor="orange"><font color="white"><b> REPORTE SUPERBLOQUE  </b></font></td><td bgcolor="orange"><font color="white"><b>   Valor   </b></font></td></tr>
 """
    fileSystem = "Ext2"

    if sb.filesystem_type == 3:
        fileSystem = "Ext3"

    vizcode += f"""    
        <tr><td>disk name</td><td>{disk_name}</td></tr>    
        <tr><td>filesystem_type</td><td>{fileSystem}</td></tr>
        <tr><td>inodes_count</td><td>{sb.inodes_count}</td></tr>
        <tr><td>blocks_count</td><td>{sb.blocks_count}</td></tr>
        <tr><td>free_blocks_count</td><td>{sb.free_blocks_count}</td></tr>
        <tr><td>free_inodes_count</td><td>{sb.free_inodes_count}</td></tr>
        <tr><td>mtime</td><td>{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sb.mtime))}</td></tr>
        <tr><td>umtime</td><td>{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sb.umtime))}</td></tr>
        <tr><td>mcount</td><td>{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sb.mcount))}</td></tr>
        <tr><td>magic</td><td>{sb.magic}</td></tr>
        <tr><td>inode_size (bytes) </td><td>{sb.inode_size}</td></tr>
        <tr><td>block_size (bytes) </td><td>{sb.block_size}</td></tr>
        <tr><td>first_ino</td><td>{sb.first_ino}</td></tr>
        <tr><td>first_blo</td><td>{sb.first_blo}</td></tr>
        <tr><td>bm_inode_start</td><td>{sb.bm_inode_start}</td></tr>
        <tr><td>bm_block_start</td><td>{sb.bm_block_start}</td></tr>
        <tr><td>inode_start</td><td>{sb.inode_start}</td></tr>
        <tr><td>block_start</td><td>{sb.block_start}</td></tr>"""

    vizcode += """    </table>>];
}
"""

    return vizcode


def get_disk_viz_code(mbr, spaces_partitions, blank_spaces, partitions, path):
    viz_code = """
    digraph structs {
    node [shape=record];
    """
    viz_code += "struct3 [label=\""

    viz_code += f"MBR &#92;n {((mbr.getMBRSize() + mbr.partition1.getPartitionSize() * 4) / mbr.size) * 100}% |"

    # Remove entries with {'size': 0, 'start_byte': -1}
    disk_free = [entry for entry in blank_spaces]
    spaces_p = [entry for entry in spaces_partitions if not (entry['size'] == 0 and entry['start_byte'] == -1)]

    disk_map = sorted(chain(disk_free, spaces_p), key=lambda x: x['start_byte'])

    for i in range(len(disk_map)):
        val = check_if_blank_space_starts(blank_spaces, disk_map[i]['start_byte'])
        if val:
            if i != len(disk_map) - 1:
                viz_code += f"LIBRE &#92;n {(val['size'] / mbr.size) * 100}% |"
            else:
                viz_code += f"LIBRE &#92;n {(val['size'] / mbr.size) * 100}%"
        else:
            found_partition = get_partition_by_byte(partitions, disk_map[i]['start_byte'])
            if found_partition.type != b'e':
                if i != len(disk_map) - 1:
                    viz_code += f"{get_type_by_initial(found_partition.type)} &#92;n {(found_partition.size / mbr.size) * 100}% |"
                else:
                    viz_code += f"{get_type_by_initial(found_partition.type)} &#92;n {(found_partition.size / mbr.size) * 100}% "
            else:
                febr = get_ebr(found_partition.start, path)
                ebr_partitions = [
                    {'size': febr.size + febr.getEBRsize(), 'start_byte': 0}
                ]

                while febr.next != -1:
                    febr = get_ebr(febr.next, path)
                    newDict = {'size': febr.size + febr.getEBRsize(),
                               'start_byte': febr.start - found_partition.start}
                    ebr_partitions.append(newDict)

                ebr_spaces = find_empty_spaces(found_partition.size, ebr_partitions)
                for space in ebr_spaces:
                    space['start_byte'] = space['start_byte'] + found_partition.start

                for space in ebr_partitions:
                    space['start_byte'] = space['start_byte'] + found_partition.start

                part_free = []
                spaces_p = []

                for entry in ebr_spaces:
                    entry['empty'] = True
                    part_free.append(entry)

                for entry in ebr_partitions:
                    entry['empty'] = False
                    spaces_p.append(entry)

                ebr_map = sorted(chain(part_free, spaces_p), key=lambda x: x['start_byte'])

                viz_code += "{"
                viz_code += "EXTENDIDA |"
                viz_code += "{"

                for j in range(len(ebr_map)):
                    if ebr_map[j]['empty']:
                        if j != len(ebr_map) - 1:
                            viz_code += f"LIBRE &#92;n {(ebr_map[j]['size'] / mbr.size) * 100}% |"
                        else:
                            viz_code += f"LIBRE &#92;n {(ebr_map[j]['size'] / mbr.size) * 100}%"
                    else:
                        if j != len(ebr_map) - 1:
                            viz_code += f"EBR &#92;n {((ebr_map[j]['size'] - febr.getEBRsize()) / mbr.size) * 100}% |"
                            viz_code += f"LOGICA &#92;n {(ebr_map[j]['size'] / mbr.size) * 100}% |"
                        else:
                            viz_code += f"EBR &#92;n {((ebr_map[j]['size'] - febr.getEBRsize()) / mbr.size) * 100}% |"
                            viz_code += f"LOGICA &#92;n {(ebr_map[j]['size'] / mbr.size) * 100}% "

                viz_code += "}"
                if i != len(disk_map) - 1:
                    viz_code += "}|"
                else:
                    viz_code += "}"

    viz_code += """
    
    "];
    
}
    """
    return viz_code


def get_partition_by_byte(partitions, byte):
    for partition in partitions:
        if partition.start == byte:
            return partition

    return None


def check_if_blank_space_starts(blank_spaces, position):
    for space in blank_spaces:
        if space['start_byte'] == position:
            return space
    return None


def get_mbr_viz_code(mbr, partitions, path):
    viz_code = """digraph G {
  rankdir=TB;
  node [shape=plaintext];
  tbl [label=<
    <table border="0" cellborder="1" cellspacing="0">
    <tr><td bgcolor="green" colspan="4"><font color="white"><b> REPORTE DE MBR </b></font></td></tr>
"""
    viz_code += f"""
        <tr>
        <td>disk size (bytes)</td>
        <td>{mbr.size}</td>
        </tr>
        
        <tr>
        <td>creation date</td>
        <td>{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mbr.creationDate))}</td>
        </tr>
        
        
        <tr>
        <td>signature</td>
        <td>{mbr.signature}</td>
        </tr>
        
        """

    for partition in partitions:
        viz_code += f"""<tr><td bgcolor="purple" colspan="4"><font color="white"><b>{"PARTICION " + get_type_by_initial(partition.type)} </b></font></td></tr>"""
        viz_code += f"""
          
        <tr>
        <td>status</td>
        <td>{partition.status.decode('utf-8')}</td>
        </tr>
        
        <tr>
        <td>type</td>
        <td>{partition.type.decode('utf-8')}</td>
        </tr>
        
        
        <tr>
        <td>fit</td>
        <td>{partition.fit.decode('utf-8')}</td>
        </tr>
        
        
        <tr>
        <td>start (byte)</td>
        <td>{partition.start}</td>
        </tr>
        
        <tr>
        <td>size (bytes)</td>
        <td>{partition.size}</td>
        </tr>
        
        
        <tr>
        <td>name</td>
        <td>{partition.name.decode('utf-8')}</td>
        </tr>
          
          """

        if partition.type == b"e":
            febr = get_ebr(partition.start, path)

            while febr.next != -1:
                viz_code += f"""<tr><td bgcolor="orange" colspan="4"><font color="white"><b>PARTICION LOGICA</b></font></td></tr>"""
                viz_code += f"""

                        <tr>
                        <td>status</td>
                        <td>{febr.status.decode('utf-8')}</td>
                        </tr>

                        <tr>
                        <td>next</td>
                        <td>{febr.next}</td>
                        </tr>


                        <tr>
                        <td>fit</td>
                        <td>{febr.fit.decode('utf-8')}</td>
                        </tr>


                        <tr>
                        <td>start (byte)</td>
                        <td>{febr.start}</td>
                        </tr>

                        <tr>
                        <td>size (bytes)</td>
                        <td>{febr.size}</td>
                        </tr>


                        <tr>
                        <td>name</td>
                        <td>{febr.name.decode('utf-8')}</td>
                        </tr>

                          """
                febr = get_ebr(febr.next, path)

            viz_code += f"""<tr><td bgcolor="orange" colspan="4"><font color="white"><b>PARTICION LOGICA</b></font></td></tr>"""
            viz_code += f"""

                        <tr>
                        <td>status</td>
                        <td>{febr.status.decode('utf-8')}</td>
                        </tr>

                        <tr>
                        <td>next</td>
                        <td>{febr.next}</td>
                        </tr>


                        <tr>
                        <td>fit</td>
                        <td>{febr.fit.decode('utf-8')}</td>
                        </tr>


                        <tr>
                        <td>start (byte)</td>
                        <td>{febr.start}</td>
                        </tr>

                        <tr>
                        <td>size (bytes)</td>
                        <td>{febr.size}</td>
                        </tr>


                        <tr>
                        <td>name</td>
                        <td>{febr.name.decode('utf-8')}</td>
                        </tr>

                          """

    viz_code += """   </table>
  >];
}"""
    return viz_code


def getMBRBypath(path):
    newmbr = MBR()
    try:
        with open(path, 'rb') as file:
            file.seek(0)
            data = file.read(newmbr.getMBRSize() + newmbr.partition1.getSerializedPartitionSize() * 4)
            newmbr.deserialize(data)
            file.close()

    except Exception as e:
        print("An error occurred:", e)
    return newmbr


def get_type_by_initial(initial):
    if initial == b"":
        return "INDEFINIDA"
    elif initial == b'p':
        return 'PRIMARIA'
    elif initial == b'e':
        return 'EXTENDIDA'
    elif initial == b'l':
        return 'LOGICA'


def get_ebr(intial_pos, path):
    ebr = EBR()
    with open(path, 'rb+') as f:
        f.seek(intial_pos)
        readed = f.read(ebr.getEBRsize())
        ebr.deserialize(readed)
        f.close()

    return ebr


def find_empty_spaces(disk_size, partitions):
    partitions = [p for p in partitions if p['size'] > 0]  # Remove undefined partitions
    partitions.sort(key=lambda x: x['start_byte'])  # Sort partitions by start_byte

    empty_spaces = []
    start_byte = 0

    for partition in partitions:
        if partition['start_byte'] > start_byte:
            empty_space_size = partition['start_byte'] - start_byte
            empty_spaces.append({'start_byte': start_byte, 'size': empty_space_size})
        start_byte = partition['start_byte'] + partition['size']

    if start_byte < disk_size:
        empty_space_size = disk_size - start_byte
        empty_spaces.append({'start_byte': start_byte, 'size': empty_space_size})

    return empty_spaces
