import struct
import ctypes

from Entities.Content import Content

const = '<i 10s i 1s'


class Folderblock(ctypes.Structure):

    def __init__(self):
        self.Content = [Content(), Content(), Content(), Content()]

    def get_infomation(self):
        print("==Folderblock info")
        print(f"Content: {self.Content}")

    def getFolderBlockSize(self):
        return struct.calcsize(const)

    def getFolderBlockSize2(self):
        return 64

    def serialize(self):
        return self.Content[0].serialize() + self.Content[1].serialize() + self.Content[2].serialize() + \
            self.Content[3].serialize()

    def deserialize(self, data):
        sizeContent = Content().getContentSize()

        for i in range(4):
            dataContent = data[(i * sizeContent): ((i + 1) * sizeContent)]
            self.Content[i] = Content()
            self.Content[i].deserialize(dataContent)
