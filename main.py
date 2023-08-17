import parser.parser


def main():
    while True:
        command = input("> ")
        parser.parser.parseString(command)


# def parseString(command):
#     parser = argparse.ArgumentParser(description="Command Parser")
#     parser.add_argument("command", help="")
#     parser.add_argument("-size", type=str, default="")
#     parser.add_argument("-path", type=str, default="")
#     parser.add_argument("-fit", type=str, default="")
#     parser.add_argument("-unit", type=str, default="")
#
#     args = parser.parse_args(shlex.split(command))
#
#     if args.command == "mkdisk":
#         newMkdisk = disk.Mkdisk("5", args.path, "ff", "m")
#         newMkdisk.createDisk()
#     elif args.command == "execute":
#         file_path = args.path
#
#         try:
#             with open(file_path, 'r') as file:
#                 for line in file:
#                     stripped_line = line.split('#', 1)[0].strip()
#                     if stripped_line:
#                         print(stripped_line)
#                         parseString(stripped_line)
#         except FileNotFoundError:
#             print(f"File '{file_path}' not found.")
#         except Exception as e:
#             print("An error occurred:", e)
#     elif args.command == 'rep':
#         try:
#             file_path = args.path
#             newmbr = MBR()
#             with open(file_path, 'rb') as file:
#                 file.seek(0)
#                 data = file.read(12)
#                 # print("Size data: ",  len(data))
#                 newmbr.deserialize(data)
#                 file.close()
#             newmbr.printData()
#
#         except Exception as e:
#             print("An error occurred:", e)


if __name__ == "__main__":
    main()
