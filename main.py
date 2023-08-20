import parser.parser


def main():
    try:
        while True:
            command = input("> ")
            parser.parser.pivote(command)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
