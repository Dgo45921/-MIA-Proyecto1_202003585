import Entities
from commands.rep import getMBRBypath


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

    partitionToModify.size = calculate_size(args.unit, args.size)
    if (bytes(args.name, 'ascii') != mbr.partition1.name and bytes(args.name, 'ascii') != mbr.partition2.name and
            bytes(args.name, 'ascii') != mbr.partition3.name and bytes(args.name, 'ascii') != mbr.partition4.name):
        partitionToModify.name = bytes(args.name, 'ascii')
    else:
        print('Error: partition name must be different than the other partitions')
        return

    if partitionToModify.size > mbr.size:
        print('Error: partition size must be less than disk size')
        return

    with open(args.path, 'rb+') as f:
        f.seek(0)
        f.write(mbr.getSerializedMBR())
        f.close()
    print('Partition setted!')


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

