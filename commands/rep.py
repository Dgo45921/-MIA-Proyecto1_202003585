from Entities.MBR import MBR
from utils.graphviz import basicMBR_report


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
        basicMBR_report(newmbr, args)



    except Exception as e:
        print("An error occurred:", e)


def getMBRBypath(path):
    newmbr = MBR()
    try:
        with open(path, 'rb') as file:
            file.seek(0)
            data = file.read(newmbr.getMBRSize() + newmbr.partition1.getSerializedPartitionSize() * 4)
            newmbr.deserialize(data)
            file.close()

    except Exception as e:
        print("An error occurred:", e)
    return newmbr
