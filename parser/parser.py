import argparse
import shlex

from Entities import disk
from Entities.MBR import MBR

parser = argparse.ArgumentParser(description="Command Parser", allow_abbrev=False)
subparsers = parser.add_subparsers(help='Available commands')


def pivote(command):
    if validate_command(command):
        # Parse the command using your existing logic
        parseString(command)


def parseString(command):
    # Parser for the mkdisk command
    mkdisk_parser = subparsers.add_parser('mkdisk', help='Create a disk')

    # Add arguments for mkdisk command
    mkdisk_parser.add_argument("-size", type=str, help="Size of the disk")
    mkdisk_parser.add_argument("-path", type=str, help="Path to save the disk")
    mkdisk_parser.add_argument("-fit", type=str.lower, default="ff", choices=['bf', 'ff', 'wf'], )
    mkdisk_parser.add_argument("-unit", default='m', type=str.lower, choices=['k', 'm'])

    # Set default command
    mkdisk_parser.set_defaults(which='mkdisk')

    # Parser for the execute command
    execute_parser = subparsers.add_parser('execute', help='Execute a task')
    execute_parser.add_argument("-path", default="")
    execute_parser.set_defaults(which='execute')

    # Parser for the rep command
    rep_parser = subparsers.add_parser('rep', help='Perform a repetition')
    rep_parser.add_argument("-path", default="")
    rep_parser.set_defaults(which='rep')

    try:
        originalComand = shlex.split(command)
        loweCasedCommand = lowerCaseCommand(originalComand)
        newStringWithLowers = ' '.join(loweCasedCommand)
        args = parser.parse_args(shlex.split(newStringWithLowers))

        if args.which == 'mkdisk':
            mkdiskCommand(args)
        elif args.which == 'execute':
            executeCommand(args)
        elif args.which == 'rep':
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
    newMkdisk = disk.Mkdisk("5", args.path, "ff", "m")
    newMkdisk.createDisk()


def repCommand(args):
    try:
        file_path = args.path
        newmbr = MBR()
        with open(file_path, 'rb') as file:
            file.seek(0)
            data = file.read(12)
            # print("Size data: ",  len(data))
            newmbr.deserialize(data)
            file.close()
        newmbr.printData()

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
