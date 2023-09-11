import argparse
import shlex

import commands
from commands.mkdisk import mkdiskCommand
from commands.rep import repCommand
from commands.fdisk import fdiskCommand
from commands.rmdisk import rmdisk
from commands.mount import mount
from commands.unmount import unmount

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
fdisk_parser.add_argument("-unit", type=str.lower, default='k', choices=['b', 'k', 'm'])
fdisk_parser.add_argument("-type", type=str.lower, default="p", choices=['p', 'e', 'l'])
fdisk_parser.add_argument("-fit", type=str.lower, default="wf", choices=['bf', 'ff', 'wf'])
fdisk_parser.add_argument("-delete", type=str, choices='full')
fdisk_parser.add_argument("-add", type=int)
fdisk_parser.set_defaults(which='fdisk')

# subparsers for rmdisk
rmdisk_parser = subparsers.add_parser('rmdisk', help='Deletes a disk')
rmdisk_parser.add_argument("-path", type=str, help="path of the disk", required=True)
rmdisk_parser.set_defaults(which='rmdisk')


# Parser for the mount command
mount_parser = subparsers.add_parser('mount')

# Add arguments for mount command
mount_parser.add_argument("-path", required=True)
mount_parser.add_argument("-name", required=True)

# Set default command
mount_parser.set_defaults(which='mount')


# Parser for the unmount command
unmount_parser = subparsers.add_parser('unmount')

# Add arguments for unmount command
unmount_parser.add_argument("-id", required=True)

# Set default command
unmount_parser.set_defaults(which='unmount')


def pivote(command):
    if validate_command(command):
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
            commands.rep.repCommand(args)
        elif args.which == 'fdisk':
            fdiskCommand(args, shlex.split(newStringWithLowers)[1])
        elif args.which == 'rmdisk':
            rmdisk(args.path)
        elif args.which == 'mount':
            mount(args.path, args.name)
        elif args.which == 'unmount':
            unmount(args.id)

    except argparse.ArgumentError as _:
        print("Error: one argument was not expected")
    except SystemExit:
        pass  # Prevent argparse from exiting the program


def lowerCaseCommand(command_args):
    for i in range(len(command_args)):
        if not (command_args[i].lower().startswith('path') or command_args[i].lower().startswith('-path') or
                command_args[i].lower().startswith('name') or command_args[i].lower().startswith('-name')):
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
                    print('Ejecutando:', stripped_line)
                    parseString(stripped_line)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
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
