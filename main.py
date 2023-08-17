import parser.parser


def main():
    while True:
        command = input("> ")
        parser.parser.pivote(command)


if __name__ == "__main__":
    main()
