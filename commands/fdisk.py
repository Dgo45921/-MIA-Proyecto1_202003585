import Entities
from Entities.EBR import EBR
from commands.rep import getMBRBypath

mbr_full_size = 121


def fdiskCommand(args, first_parameter):
    if args.size <= 0:
        print('Error: size of partition must be greater than 0!')
        return
    if first_parameter.startswith('-delete=full'):
        deletePartition(args)
        return
    elif first_parameter.startswith('-add'):
        mbr = getMBRBypath(args.path)
        index = 0

        partitions = [
            {'size': mbr_full_size, 'start_byte': 0},
            {'size': mbr.partition1.size, 'start_byte': mbr.partition1.start},
            {'size': mbr.partition2.size, 'start_byte': mbr.partition2.start},
            {'size': mbr.partition3.size, 'start_byte': mbr.partition3.start},
            {'size': mbr.partition4.size, 'start_byte': mbr.partition4.start}
        ]

        if bytes(args.name, 'ascii') == mbr.partition1.name:
            index = 1
        elif bytes(args.name, 'ascii') == mbr.partition2.name:
            index = 2
        elif bytes(args.name, 'ascii') == mbr.partition3.name:
            index = 3
        elif bytes(args.name, 'ascii') == mbr.partition4.name:
            index = 4

        if index == 0:
            print('Error: Partition not found!')
            return

        if args.add >= 0:
            additional_size_in_bytes = calculate_size(args.unit, args.add)
            add_space(mbr, index, additional_size_in_bytes, mbr.size, args, partitions)
        else:
            space_to_be_free = calculate_size(args.unit, args.add)
            delete_space(mbr, index, space_to_be_free * -1, mbr.size, args, partitions)
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
    if partitionToModify is None:
        print('Error: partition not found!')
        return

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
    if args.type == 'p' or args.type == 'e':
        if default_partition.equalToDefault(mbr.partition1):
            partitionToModify = mbr.partition1
        elif default_partition.equalToDefault(mbr.partition2):
            partitionToModify = mbr.partition2
        elif default_partition.equalToDefault(mbr.partition3):
            partitionToModify = mbr.partition3
        elif default_partition.equalToDefault(mbr.partition4):
            partitionToModify = mbr.partition4
        else:
            print("There is no space available for a new primary or extended partition!")
            return

        partitionToModify.status = bytes('1', 'ascii')
        partitionToModify.fit = bytes(args.fit[0], 'ascii')
        if (bytes(args.name, 'ascii') != mbr.partition1.name and bytes(args.name, 'ascii') != mbr.partition2.name and
                bytes(args.name, 'ascii') != mbr.partition3.name and bytes(args.name, 'ascii') != mbr.partition4.name):
            partitionToModify.name = bytes(args.name, 'ascii')
        else:
            foundExtended = False
            if b'e' == mbr.partition1.type:
                partitionToModify = mbr.partition1
                foundExtended = True

            elif b'e' == mbr.partition2.type:
                partitionToModify = mbr.partition2
                foundExtended = True
            elif b'e' == mbr.partition3.type:
                partitionToModify = mbr.partition3
                foundExtended = True
            elif b'e' == mbr.partition4.type:
                partitionToModify = mbr.partition4
                foundExtended = True

            if foundExtended:
                first_ebr = get_ebr(partitionToModify.start, args.path)
                while first_ebr.next != -1:
                    if first_ebr.name == bytes(args.name, 'ascii'):
                        print('Error: partition name must be different than the other partitions')
                        return
                    first_ebr = get_ebr(first_ebr.next, args.path)

        if args.type == 'e':

            if (b'e' != mbr.partition1.type and b'e' != mbr.partition2.type and
                    b'e' != mbr.partition3.type and b'e' != mbr.partition4.type):
                partitionToModify.type = bytes(args.type, 'ascii')
            else:
                print('Error: There can only be one extended partition in the disk')
                return

        partitionToModify.type = bytes(args.type, 'ascii')
        partitions = [
            {'size': mbr_full_size, 'start_byte': 0},
            {'size': mbr.partition1.size, 'start_byte': mbr.partition1.start},
            {'size': mbr.partition2.size, 'start_byte': mbr.partition2.start},
            {'size': mbr.partition3.size, 'start_byte': mbr.partition3.start},
            {'size': mbr.partition4.size, 'start_byte': mbr.partition4.start}
        ]
        if mbr.fit == b'F':
            print('F')
            pos = get_first_fit_position(mbr.size, partitionToModify, args, partitions)
            if pos == -1:
                print('Error: no space available')
                return

            partitionToModify.start = pos
            print('the starting byte will be: ', pos)
        elif mbr.fit == b'W':
            print('W')
            pos = get_worst_fit_position(mbr.size, partitionToModify, args, partitions)
            if pos == -1:
                print('Error: no space available')
                return

            partitionToModify.start = pos
            print('the starting byte will be: ', pos)
        elif mbr.fit == b'B':
            print('B')
            pos = get_best_fit_position(mbr.size, partitionToModify, args, partitions)
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

        if partitionToModify.type == b'e':
            new_ebr = EBR()
            with open(args.path, 'rb+') as f:
                f.seek(partitionToModify.start)
                f.write(new_ebr.getSerializedEBR())
                f.close()

        print('Partition setted!')

    elif args.type == 'l':

        if (bytes(args.name, 'ascii') == mbr.partition1.name or bytes(args.name, 'ascii') == mbr.partition2.name or
                bytes(args.name, 'ascii') == mbr.partition3.name or bytes(args.name, 'ascii') == mbr.partition4.name):
            print('Error, logical partition has the same name of another partition!')
            return

        foundExtended = False
        if b'e' == mbr.partition1.type:
            partitionToModify = mbr.partition1
            foundExtended = True

        elif b'e' == mbr.partition2.type:
            partitionToModify = mbr.partition2
            foundExtended = True
        elif b'e' == mbr.partition3.type:
            partitionToModify = mbr.partition3
            foundExtended = True
        elif b'e' == mbr.partition4.type:
            partitionToModify = mbr.partition4
            foundExtended = True

        if foundExtended:
            first_ebr = get_ebr(partitionToModify.start, args.path)
            first_partition = first_ebr.equalToDefault(EBR())
            pointer = partitionToModify.start
            while first_ebr.next != -1:
                if first_ebr.name == bytes(args.name, 'ascii'):
                    print('Error, logical partition has the same name of another partition!')
                    return
                first_ebr = get_ebr(first_ebr.next, args.path)
                pointer += first_ebr.size

            while first_ebr.next != -1:
                first_ebr = get_ebr(first_ebr.next, args.path)
                pointer += first_ebr.size

            if first_partition:
                first_ebr.start = pointer
                first_ebr.size = calculate_size(args.unit, args.size)
                first_ebr.fit = bytes(args.fit[0], 'ascii')
                first_ebr.name = bytes(args.name, 'ascii')
                first_ebr.status = b'1'
                if first_ebr.start + first_ebr.size > partitionToModify.start + partitionToModify.size:
                    if first_ebr.next != -1 and first_ebr.start + first_ebr.size > first_ebr.next:
                        print("Error, logical partition is too big to add in the extended partition")
                        return

                    print("Error, logical partition is too big to add in the extended partition")
                    return

                with open(args.path, 'rb+') as f:
                    f.seek(first_ebr.start)
                    f.write(first_ebr.getSerializedEBR())
                    return

            else:
                next_ebr = EBR()
                next_ebr.start = first_ebr.start + first_ebr.getEBRsize() + first_ebr.size
                first_ebr.next = next_ebr.start
                next_ebr.name = bytes(args.name, 'ascii')
                next_ebr.fit = bytes(args.fit[0], 'ascii')
                next_ebr.size = args.size
                next_ebr.status = b'1'

                if next_ebr.start + next_ebr.size > partitionToModify.start + partitionToModify.size:
                    print("Error, logical partition is too big to add in the extended partition")

                with open(args.path, 'rb+') as f:
                    f.seek(first_ebr.start)
                    f.write(first_ebr.getSerializedEBR())
                    f.seek(next_ebr.start)
                    f.write(next_ebr.getSerializedEBR())
                    f.close()
                return

        else:
            print('No extended partition to add this logical partition was found!')
            return


def get_first_fit_position(size, target_partition, args, partitions):
    final_pos = -1

    blank_spaces = find_empty_spaces(size, partitions)
    target_partition.size = calculate_size(args.unit, args.size)

    for empty_space in blank_spaces:
        if empty_space['size'] >= target_partition.size:
            final_pos = empty_space['start_byte']
            break

    return final_pos


def get_best_fit_position(size, target_partition, args, partitions):
    blank_spaces = find_empty_spaces(size, partitions)
    target_partition.size = calculate_size(args.unit, args.size)

    filtered_dicts = [d for d in blank_spaces if d['size'] <= target_partition.size]
    if filtered_dicts:
        dict_with_smallest_size = min(filtered_dicts, key=lambda x: x['size'])
        return dict_with_smallest_size['start_byte']
    else:
        return -1


def get_worst_fit_position(size, target_partition, args, partitions):
    blank_spaces = find_empty_spaces(size, partitions)
    target_partition.size = calculate_size(args.unit, args.size)

    filtered_dicts = [d for d in blank_spaces if d['size'] >= target_partition.size]
    if filtered_dicts:
        dict_with_largest_size = max(filtered_dicts, key=lambda x: x['size'])
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


def delete_space(mbr, partition_index, size_to_delete, disk_size, args, partitions):
    if partition_index < 0 or partition_index >= len(partitions):
        print("Invalid partition index.")
        return

    partition = partitions[partition_index]

    # Ignore undefined partitions
    if partition['size'] == 0:
        print("Cannot delete space from an undefined partition.")
        return

    if size_to_delete < partition['size']:
        fileIndex = partition['start_byte'] + (partition['size'] - size_to_delete)
        partition['size'] -= size_to_delete
    else:
        print('cannot delete more of the size partition')
        return

    if partition['start_byte'] + partition['size'] > disk_size:
        print("Partition size after deletion exceeds disk size.")
        return

    mbr.partition1.size = partitions[1]['size']
    mbr.partition1.start = partitions[1]['start_byte']

    mbr.partition2.size = partitions[2]['size']
    mbr.partition2.start = partitions[2]['start_byte']

    mbr.partition3.size = partitions[3]['size']
    mbr.partition3.start = partitions[3]['start_byte']

    mbr.partition4.size = partitions[4]['size']
    mbr.partition4.start = partitions[4]['start_byte']

    with open(args.path, 'rb+') as f:
        f.seek(0)
        f.write(mbr.getSerializedMBR())
        f.seek(fileIndex)
        f.write(b'\x00' * size_to_delete)

        f.close()

    print(f'Partition: {args.name}\' size decreased: {size_to_delete} bytes')


def add_space(mbr, partition_index, additional_size, disk_size, args, partitions):
    if partition_index < 0 or partition_index >= len(partitions):
        print("Invalid partition index.")
        return

    partition = partitions[partition_index]

    # Ignore undefined partitions
    if partition['size'] == 0:
        print("Cannot add space to an undefined partition.")
        return

    new_size = partition['size'] + additional_size

    next_defined_partition_index = partition_index + 1
    while next_defined_partition_index < len(partitions) and partitions[next_defined_partition_index]['size'] == 0:
        next_defined_partition_index += 1

    if next_defined_partition_index < len(partitions) and partition['start_byte'] + new_size > \
            partitions[next_defined_partition_index]['start_byte']:
        print("Space addition would overlap with next partition.")
        return

    if partition['start_byte'] + new_size > disk_size:
        print("Space addition would exceed disk size.")
        return

    partition['size'] = new_size
    mbr.partition1.size = partitions[1]['size']
    mbr.partition1.start = partitions[1]['start_byte']

    mbr.partition2.size = partitions[2]['size']
    mbr.partition2.start = partitions[2]['start_byte']

    mbr.partition3.size = partitions[3]['size']
    mbr.partition3.start = partitions[3]['start_byte']

    mbr.partition4.size = partitions[4]['size']
    mbr.partition4.start = partitions[4]['start_byte']

    with open(args.path, 'rb+') as f:
        f.seek(0)
        f.write(mbr.getSerializedMBR())

        f.seek(partitions[partition_index]['start_byte'] + partitions[partition_index]['size'] + additional_size)
        f.write(b'\x00' * additional_size)

        f.close()

    print(f'Partition: {args.name}\' size increased: {additional_size} bytes')


def get_ebr(intial_pos, path):
    ebr = EBR()
    with open(path, 'rb+') as f:
        f.seek(intial_pos)
        readed = f.read(ebr.getEBRsize())
        ebr.deserialize(readed)
        f.close()

    return ebr
