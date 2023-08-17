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
        if not self.size.isdigit():
            print('Error: size parameter must be a number')
            return

        # writing 5mb of pure 0's bytes
        if self.units == 'm':
            file_size = int(self.size) * 1024 * 1024  # 5MB
            byte_value = b'\x00'
            directory = os.path.dirname(self.path)
            os.makedirs(directory, exist_ok=True)

            with open(self.path, 'wb') as f:
                f.write(byte_value * file_size)
                f.close()

        # creating mbr
        self.mbr = MBR()
        self.mbr.setSize(int(self.size) * 1024 * 1024)

        with open(self.path, 'rb+') as f:
            f.seek(0)
            # print(self.mbr.size)
            # print(self.mbr.creationDate)
            # print(self.mbr.signature)

            f.write(self.mbr.getSerializedMBR())
            f.close()
            print('The disk was created succesfully!')

