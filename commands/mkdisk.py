from Entities import disk


def mkdiskCommand(args):
    newMkdisk = disk.Mkdisk(args.size, args.path, args.fit, args.unit)
    newMkdisk.createDisk()
