import os
import time
from itertools import chain

from Entities.EBR import EBR
from Entities.MBR import MBR
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
        os.system("dot -Tjpg \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"'+output_path+'"')
    elif file_name.endswith('.png'):
        os.system("dot -Tpng \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"'+ output_path+'"')
    elif file_name.endswith('.pdf'):
        os.system("dot -Tpdf \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"'+ output_path+'"')

    os.system('rm \"' + directory + "/" + file_name.split('.')[0] + '.dot\"')
    print(f'mbr report generated in{directory}')


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
        os.system("dot -Tjpg \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"'+ output_path+'"' )
    elif file_name.endswith('.png'):
        os.system("dot -Tpng \"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " +'"'+ output_path+'"')
    elif file_name.endswith('.pdf'):
        os.system("dot -Tpdf\"" + directory + "/" + file_name.split('.')[0] + '.dot\"' + " -o " + '"'+output_path+'"')

    os.system('rm "' + directory + "/" + file_name.split('.')[0] + '.dot\"')
    print(f'disk report generated in{directory}')


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
                    viz_code += f"{get_type_by_initial(found_partition.type)} &#92;n {(found_partition.size/mbr.size) * 100}% |"
                else:
                    viz_code += f"{get_type_by_initial(found_partition.type)} &#92;n {(found_partition.size/mbr.size) * 100}% "
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
    <tr><td bgcolor="red" colspan="4"><font color="white"><b> REPORTE MBR </b></font></td></tr>
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
        viz_code += f"""<tr><td bgcolor="red" colspan="4"><font color="white"><b>{"PARTICION " + get_type_by_initial(partition.type)} </b></font></td></tr>"""
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
