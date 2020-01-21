import sys
from you_tube_common import get_event_info, compile_mp4_video_from_audio


def main():
    event_id = 1382
    event_info = get_event_info(event_id)
    if event_info["drive_audio_id"] is not None:
        video_file_name = compile_mp4_video_from_audio(event_info)
        if video_file_name is None:
            sys.tracebacklimit = 0
            raise Exception(("Not able to download/convert file DriveID={} from " +
                             "eventID={}.").format(event_info["drive_audio_id"], event_id))
    else:
        sys.tracebacklimit = 0
        raise Exception(("No edited audio file is available to compile video for " +
                         "eventID={}.").format(event_id))
    print(event_info)


if __name__ == '__main__':
    main()

# Version 1.0
