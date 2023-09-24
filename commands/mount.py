import os

from Entities.EBR import EBR
from Entities.MBR import MBR

id_const = '85'
mounted_partitions = []


def mount(path, name):
    if not path.endswith('.dsk'):
        print('Error, file type must be a .dsk file')
        return

    try:
        found_mbr = MBR()
        with open(path, 'rb') as file:
            file.seek(0)
            data = file.read(found_mbr.getMBRSize() + found_mbr.partition1.getSerializedPartitionSize() * 4)
            found_mbr.deserialize(data)
            file.close()

        partitions = [found_mbr.partition1, found_mbr.partition2, found_mbr.partition3, found_mbr.partition4]
        file_name = os.path.basename(path).split('.')[0]
        found_partition = get_dict(partitions, name, path, file_name)
        if found_partition is None:
            print('Error, partition not found')
            return

        value_to_check = found_partition['id']
        found_partition['disk_path'] = path

        exists = any(partition['id'] == value_to_check for partition in mounted_partitions)

        if exists:
            print(f"Partition '{value_to_check}' already mounted")
        else:
            mounted_partitions.append(found_partition)
            print('mounted partitions: ')
            for partition in mounted_partitions:
                print(partition['id'])




    except Exception as e:
        print("An error occurred:", e)


def get_dict(partitions, name, path, disk_name):
    index = 0
    for partition in partitions:
        index += 1
        if b'e' == partition.type or bytes(name, 'ascii') == partition.name:
            if b'e' == partition.type:
                if bytes(name, 'ascii') == partition.name:
                    return {'id': id_const + str(index) + disk_name, 'partition': partition}
                current_ebr = get_ebr(partition.start, path)
                if current_ebr.next != 1:
                    while current_ebr.next != -1:
                        if current_ebr.name == bytes(name, 'ascii'):
                            return {'id': id_const + str(index) + disk_name, 'partition': current_ebr}

                        current_ebr = get_ebr(current_ebr.next, path)
                        index += 1
                    if current_ebr.name == bytes(name, 'ascii'):
                        return {'id': id_const + str(index) + disk_name, 'partition': current_ebr}
                else:
                    if current_ebr.name == bytes(name, 'ascii'):
                        return {'id': id_const + str(index) + disk_name, 'partition': current_ebr}
            else:

                return {'id': id_const + str(index) + disk_name, 'partition': partition}

    return None


def get_ebr(intial_pos, path):
    ebr = EBR()
    with open(path, 'rb+') as f:
        f.seek(intial_pos)
        readed = f.read(ebr.getEBRsize())
        ebr.deserialize(readed)
        f.close()

    return ebr


def get_mounted_partition(id_):
    matching_partition = next((partition for partition in mounted_partitions if partition['id'] == id_),
                              None)

    if matching_partition is not None:
        return matching_partition
    else:
        return None
