from you_tube_common import get_event_info


def main():
    event_info = get_event_info(1319)
    print(event_info, "\n")
    for key in event_info:
        print("{}: {}".format(key, event_info[key]))


if __name__ == '__main__':
    main()

# Version 1.0
