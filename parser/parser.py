import argparse
import shlex

from Entities import disk
from Entities.MBR import MBR

parser = argparse.ArgumentParser(description="Command Parser", allow_abbrev=False)
subparsers = parser.add_subparsers(help='Available commands')

# Parser for the mkdisk command
mkdisk_parser = subparsers.add_parser('mkdisk', help='Create a disk')

# Add arguments for mkdisk command
mkdisk_parser.add_argument("-size", type=int, help="Size of the disk", required=True)
mkdisk_parser.add_argument("-path", type=str, help="Path to save the disk", required=True)
mkdisk_parser.add_argument("-fit", type=str.lower, default="ff", choices=['bf', 'ff', 'wf'])
mkdisk_parser.add_argument("-unit", default='m', type=str.lower, choices=['k', 'm'])

# Set default command
mkdisk_parser.set_defaults(which='mkdisk')

# Parser for the execute command
execute_parser = subparsers.add_parser('execute')
execute_parser.add_argument("-path", default="")
execute_parser.set_defaults(which='execute')

# Parser for the rep command
rep_parser = subparsers.add_parser('rep')
rep_parser.add_argument("-path", default="")
rep_parser.set_defaults(which='rep')

fdisk_parser = subparsers.add_parser('fdisk', help='Create a partition')

# Add arguments for fdisk command
fdisk_parser.add_argument("-size", type=int, help="Size of the disk", required=True)
fdisk_parser.add_argument("-path", type=str, help="Path to save the disk", required=True)
fdisk_parser.add_argument("-name", type=str, help="Path to save the disk", required=True)
fdisk_parser.add_argument("-unit",  type=str.lower, default='k', choices=['b', 'k', 'm'])
fdisk_parser.add_argument("-type", type=str.lower,  default="p", choices=['p', 'e', 'l'])
fdisk_parser.add_argument("-fit", type=str.lower,  default="wf", choices=['bf', 'ff', 'wf'])
fdisk_parser.add_argument("-delete", type=str)
fdisk_parser.add_argument("-add", type=int)
fdisk_parser.set_defaults(which='fdisk')


def pivote(command):
    if validate_command(command):
        # Parse the command using your existing logic
        parseString(command)


def parseString(command):
    try:
        originalComand = shlex.split(command)
        lower_cased_command = lowerCaseCommand(originalComand)
        newStringWithLowers = ' '.join(lower_cased_command)
        args = parser.parse_args(shlex.split(newStringWithLowers))

        if args.which == 'mkdisk':
            mkdiskCommand(args)
        elif args.which == 'execute':
            executeCommand(args)
        elif args.which == 'rep':
            repCommand(args)
        elif args.which == 'fdisk':
            repCommand(args)
    except argparse.ArgumentError as _:
        print("Error: one argument was not expected")
    except SystemExit:
        pass  # Prevent argparse from exiting the program


def lowerCaseCommand(command_args):
    for i in range(len(command_args)):
        if not (command_args[i].lower().startswith('path') or command_args[i].lower().startswith('-path')):
            command_args[i] = command_args[i].lower()
        else:
            splitted_path = command_args[i].split('=')
            splitted_path[0] = splitted_path[0].lower()
            if " " in splitted_path[1]:
                command_args[i] = command_args[i].replace(splitted_path[1], '"' + splitted_path[1] + '"')

    return command_args


def executeCommand(args):
    file_path = args.path

    try:
        with open(file_path, 'r') as file:
            for line in file:
                stripped_line = line.split('#', 1)[0].strip()
                if stripped_line:
                    print(stripped_line)
                    parseString(stripped_line)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print("An error occurred:", e)


def mkdiskCommand(args):
    newMkdisk = disk.Mkdisk(args.size, args.path, args.fit, args.unit)
    newMkdisk.createDisk()


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

    except Exception as e:
        print("An error occurred:", e)


def validate_command(command):
    arguments = shlex.split(command)

    for arg in arguments[1:]:
        parts = arg.split('=')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            print(f"Error: Invalid argument format")
            return False
    return True
