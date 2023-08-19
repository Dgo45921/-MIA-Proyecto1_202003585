import Entities
from commands.rep import getMBRBypath

mbr_full_size = 121


def fdiskCommand(args, first_parameter):
    if args.size <= 0:
        print('Error: size of partition must be greater than 0!')
        return
    if first_parameter.startswith('-delete=full'):
        deletePartition(args)
    elif first_parameter.startswith('-add'):
        pass
    else:
        createPartition(args)
        return


def deletePartition(args):
    mbr = getMBRBypath(args.path)
    partitionToModify = None
    byes_to_write = 0

    if bytes(args.name, 'ascii') == mbr.partition1.name:
        partitionToModify = mbr.partition1
        byes_to_write = mbr.partition1.size
        mbr.partition1 = Entities.Partition.Partition()
    elif bytes(args.name, 'ascii') == mbr.partition2.name:
        partitionToModify = mbr.partition2
        byes_to_write = mbr.partition2.size
        mbr.partition2 = Entities.Partition.Partition()
    elif bytes(args.name, 'ascii') == mbr.partition3.name:
        partitionToModify = mbr.partition3
        byes_to_write = mbr.partition3.size
        mbr.partition3 = Entities.Partition.Partition()
    elif bytes(args.name, 'ascii') == mbr.partition4.name:
        partitionToModify = mbr.partition4
        byes_to_write = mbr.partition4.size
        mbr.partition4 = Entities.Partition.Partition()

    with open(args.path, 'rb+') as f:
        f.seek(partitionToModify.start)
        f.write(b'\x00' * byes_to_write)
        f.seek(0)
        f.write(mbr.getSerializedMBR())
        f.close()
    print('Partition deleted!')


def createPartition(args):
    default_partition = Entities.Partition.Partition()
    mbr = getMBRBypath(args.path)
    partitionToModify = None

    if default_partition.equalToDefault(mbr.partition1):
        partitionToModify = mbr.partition1
    elif default_partition.equalToDefault(mbr.partition2):
        partitionToModify = mbr.partition2
    elif default_partition.equalToDefault(mbr.partition3):
        partitionToModify = mbr.partition3
    elif default_partition.equalToDefault(mbr.partition4):
        partitionToModify = mbr.partition4

    partitionToModify.status = bytes('1', 'ascii')
    partitionToModify.type = bytes(args.type, 'ascii')
    partitionToModify.fit = bytes(args.fit, 'ascii')
    if (bytes(args.name, 'ascii') != mbr.partition1.name and bytes(args.name, 'ascii') != mbr.partition2.name and
            bytes(args.name, 'ascii') != mbr.partition3.name and bytes(args.name, 'ascii') != mbr.partition4.name):
        partitionToModify.name = bytes(args.name, 'ascii')
    else:
        print('Error: partition name must be different than the other partitions')
        return

    if (
            partitionToModify.type == b'e' and partitionToModify.type != mbr.partition1.type and partitionToModify.type != mbr.partition2.type and
            partitionToModify.type != mbr.partition3.type and partitionToModify.type != mbr.partition4.type):
        partitionToModify.name = bytes(args.name, 'ascii')
    else:
        print('Error: There can only be one extended partition in the disk')
        return

    if mbr.fit == b'F':
        print('F')
        pos = get_first_fit_position(mbr, partitionToModify, args)
        if pos == -1:
            print('Error: no space available')
            return

        partitionToModify.start = pos
        print('the starting byte will be: ', pos)
    elif mbr.fit == b'W':
        print('W')
        pos = get_worst_fit_position(mbr, partitionToModify, args)
        if pos == -1:
            print('Error: no space available')
            return

        partitionToModify.start = pos
        print('the starting byte will be: ', pos)
    elif mbr.fit == b'B':
        print('B')
        pos = get_best_fit_position(mbr, partitionToModify, args)
        if pos == -1:
            print('Error: no space available')
            return

        partitionToModify.start = pos
        print('the starting byte will be: ', pos + 1)

    if partitionToModify.size > mbr.size - mbr_full_size:
        print('Error: partition size must be less than disk size')
        return

    with open(args.path, 'rb+') as f:
        f.seek(0)
        f.write(mbr.getSerializedMBR())
        f.close()
    print('Partition setted!')


def get_first_fit_position(mbr, target_partition, args):
    final_pos = -1
    partitions = [
        {'size': mbr_full_size, 'start_byte': 0},
        {'size': mbr.partition1.size, 'start_byte': mbr.partition1.start},
        {'size': mbr.partition2.size, 'start_byte': mbr.partition2.start},
        {'size': mbr.partition3.size, 'start_byte': mbr.partition3.start},
        {'size': mbr.partition4.size, 'start_byte': mbr.partition4.start}
    ]
    blank_spaces = find_empty_spaces(mbr.size, partitions)
    target_partition.size = calculate_size(args.unit, args.size)

    for empty_space in blank_spaces:
        if empty_space['size'] >= target_partition.size:
            final_pos = empty_space['start_byte']
            break

    return final_pos


def get_best_fit_position(mbr, target_partition, args):
    partitions = [
        {'size': mbr_full_size, 'start_byte': 0},
        {'size': mbr.partition1.size, 'start_byte': mbr.partition1.start},
        {'size': mbr.partition2.size, 'start_byte': mbr.partition2.start},
        {'size': mbr.partition3.size, 'start_byte': mbr.partition3.start},
        {'size': mbr.partition4.size, 'start_byte': mbr.partition4.start}
    ]
    blank_spaces = find_empty_spaces(mbr.size, partitions)
    target_partition.size = calculate_size(args.unit, args.size)

    filtered_dicts = [d for d in blank_spaces if d['size'] <= target_partition.size]
    if filtered_dicts:
        dict_with_smallest_size = min(filtered_dicts, key=lambda x: x['size'])
        print(dict_with_smallest_size)
        return dict_with_smallest_size['start_byte']
    else:
        return -1


def get_worst_fit_position(mbr, target_partition, args):
    partitions = [
        {'size': mbr_full_size, 'start_byte': 0},
        {'size': mbr.partition1.size, 'start_byte': mbr.partition1.start},
        {'size': mbr.partition2.size, 'start_byte': mbr.partition2.start},
        {'size': mbr.partition3.size, 'start_byte': mbr.partition3.start},
        {'size': mbr.partition4.size, 'start_byte': mbr.partition4.start}
    ]
    blank_spaces = find_empty_spaces(mbr.size, partitions)
    target_partition.size = calculate_size(args.unit, args.size)

    filtered_dicts = [d for d in blank_spaces if d['size'] >= target_partition.size]
    if filtered_dicts:
        dict_with_largest_size = max(filtered_dicts, key=lambda x: x['size'])
        print(dict_with_largest_size)
        return dict_with_largest_size['start_byte']
    else:
        return -1


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


def calculate_size(size_type, value):
    kilobyte = 1024
    megabyte = kilobyte * 1024

    if size_type == 'k':
        result = value * kilobyte
    elif size_type == 'm':
        result = value * megabyte
    elif size_type == 'b':
        result = value
    else:
        return "Invalid size type. Please use 'k', 'm', or 'b'."

    return result
