from you_tube_common import get_event_info, compile_custom_thumbnail


def main():
    event_info = get_event_info(1436)
    print(event_info, "\n")
    file_name = compile_custom_thumbnail(event_info)
    print(file_name)


if __name__ == '__main__':
    main()

# Version 1.0
