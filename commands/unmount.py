from commands.mount import mounted_partitions


def unmount(id_):
    for i in range(len(mounted_partitions)):
        if mounted_partitions[i]['id'] == id_:
            mounted_partitions.pop(i)
            break
    print('mounted partitions: ')
    for partition in mounted_partitions:
        print(partition['id'])

