from commands.mount import mounted_partitions


def unmount(id_):
    unmounted = False
    for i in range(len(mounted_partitions)):
        if mounted_partitions[i]['id'] == id_:
            mounted_partitions.pop(i)
            unmounted = True
            break

    if unmounted:
        print('mounted partitions: ')
        for partition in mounted_partitions:
            print(partition['id'])
        return
    print(f"No mounted partition with id: {id_}")
