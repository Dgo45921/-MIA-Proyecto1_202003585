import os
import time

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
        pass
    elif file_name.endswith('.png'):
        os.system("dot -Tpng " + directory + "/" + file_name.split('.')[0] + '.dot' + " -o " + output_path)
    elif file_name.endswith('.pdf'):
        pass



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
