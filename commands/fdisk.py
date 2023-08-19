import Entities
from commands.rep import getMBRBypath

mbr_full_size = 121


def fdiskCommand(args):
    if args.size <= 0:
        print('Error: size of partition must be greater than 0!')
        return

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

    if (bytes(args.name, 'ascii') != mbr.partition1.name and bytes(args.name, 'ascii') != mbr.partition2.name and
            bytes(args.name, 'ascii') != mbr.partition3.name and bytes(args.name, 'ascii') != mbr.partition4.name):
        partitionToModify.name = bytes(args.name, 'ascii')
    else:
        print('Error: partition name must be different than the other partitions')
        return

    if mbr.fit == b'F':
        print('F')
        pos = get_first_fit_position(mbr, partitionToModify, args)
        if pos == -1:
            print('Error: no space available')
            return

        partitionToModify.start = pos + mbr_full_size + 1
        print('the starting byte will be: ', pos + mbr_full_size + 1)
    elif mbr.fit == b'W':
        print('W')
        pos = get_worst_fit_position(mbr, partitionToModify, args)
        if pos == -1:
            print('Error: no space available')
            return

        partitionToModify.start = pos + mbr_full_size + 1
        print('the starting byte will be: ', pos + mbr_full_size + 1)
    elif mbr.fit == b'B':
        print('B')
        pos = get_best_fit_position(mbr, partitionToModify, args)
        if pos == -1:
            print('Error: no space available')
            return

        partitionToModify.start = pos + mbr_full_size + 1
        print('the starting byte will be: ', pos + mbr_full_size + 1)

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
        {'size': mbr.partition1.size, 'start_byte': mbr.partition1.start - mbr_full_size},
        {'size': mbr.partition2.size, 'start_byte': mbr.partition2.start - mbr_full_size},
        {'size': mbr.partition3.size, 'start_byte': mbr.partition3.start - mbr_full_size},
        {'size': mbr.partition4.size, 'start_byte': mbr.partition4.start - mbr_full_size}
    ]
    blank_spaces = find_empty_spaces(mbr.size, partitions)
    target_partition.size = calculate_size(args.unit, args.size)

    for empty_space in blank_spaces:
        if empty_space['size'] >= target_partition.size:
            final_pos = empty_space['start_byte']
            break

    return final_pos


def get_best_fit_position(mbr, target_partition, args):
    final_pos = -1
    partitions = [
        {'size': mbr.partition1.size, 'start_byte': mbr.partition1.start - mbr_full_size},
        {'size': mbr.partition2.size, 'start_byte': mbr.partition2.start - mbr_full_size},
        {'size': mbr.partition3.size, 'start_byte': mbr.partition3.start - mbr_full_size},
        {'size': mbr.partition4.size, 'start_byte': mbr.partition4.start - mbr_full_size}
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
        {'size': mbr.partition1.size, 'start_byte': mbr.partition1.start - mbr_full_size},
        {'size': mbr.partition2.size, 'start_byte': mbr.partition2.start - mbr_full_size},
        {'size': mbr.partition3.size, 'start_byte': mbr.partition3.start - mbr_full_size},
        {'size': mbr.partition4.size, 'start_byte': mbr.partition4.start - mbr_full_size}
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
