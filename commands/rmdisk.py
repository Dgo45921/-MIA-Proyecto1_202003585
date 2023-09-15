import os


def rmdisk(path: str):
    while True:
        if path.endswith('.dsk'):
            if not os.path.exists(path):
                print(f'The file in: {path} does not exists')
                return
            response = input(f'Are you sure you want to delete: {path} ? (y/n) \n')
            if response == 'y' or response == 'Y':
                os.remove(path)
                print(f'Disk {path} deleted')
                break
            elif response == 'N' or response == 'n':
                break
            else:
                continue
        else:
            print('Error: invalid extension of disk!')
