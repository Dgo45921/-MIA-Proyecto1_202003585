import os

from Entities.MBR import MBR


class Mkdisk:
    def __init__(self, size, path, fit, units):
        self.size: str = size
        self.path: str = path
        self.fit: str = fit
        self.units: str = units
        self.mbr = None

    def createDisk(self):
        if self.size == 0:
            print('Error: size parameter must be an integer greater than 0')
            return
        if not self.path.endswith('.dsk'):
            print('Error: extension must be ".dsk"')
            return

        file_size = 0
        # creating mbr
        self.mbr = MBR()

        if self.units == 'm':
            file_size = int(self.size) * 1024 * 1024  # MB
            self.mbr.setAttributes(int(self.size) * 1024 * 1024, self.fit[0].upper())
        else:
            file_size = int(self.size) * 1024  # KB
            self.mbr.setAttributes(int(self.size) * 1024, self.fit[0].upper())

        byte_value = b'\x00'
        directory = os.path.dirname(self.path)
        os.makedirs(directory, exist_ok=True)

        with open(self.path, 'wb') as f:
            f.write(byte_value * file_size)
            f.close()




        with open(self.path, 'rb+') as f:
            f.seek(0)
            # print(self.mbr.size)
            # print(self.mbr.creationDate)
            # print(self.mbr.signature)

            f.write(self.mbr.getSerializedMBR())
            f.close()
            print('The disk was created succesfully!')
