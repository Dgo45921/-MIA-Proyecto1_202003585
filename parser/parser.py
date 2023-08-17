import argparse
import shlex

from Entities import disk
from Entities.MBR import MBR


def parseString(command):
    parser = argparse.ArgumentParser(description="Command Parser")
    subparsers = parser.add_subparsers(help='Available commands')

    # Parser for the mkdisk command
    mkdisk_parser = subparsers.add_parser('mkdisk', help='Create a disk')
    mkdisk_parser.add_argument("-size", type=str, default="")
    mkdisk_parser.add_argument("-path", type=str, default="")
    mkdisk_parser.add_argument("-fit", type=str, default="")
    mkdisk_parser.add_argument("-unit", type=str, default="")
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
        args = parser.parse_args(shlex.split(command))
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
