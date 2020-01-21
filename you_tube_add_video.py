from __future__ import print_function
import sys

from googleapiclient import discovery, errors
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools
from you_tube_common import get_all_video_info

# This program will upload a video to YouTube
#
# If you run this script and there are no credentials or
# credentials are invalid, you need to run the script like:
# python3 ./get_media_id.py --noauth_local_webserver
#
# The script will generate a url for you to run on a machine with
# a Browser, a verification code will be generated. Enter the code
# on this machine and credentials will be updated. Next time you
# can run the script normally.


def add_video(creds, event_id, notify=True, privacy_status="public", pub_type=1):
    # https://developers.google.com/youtube/v3/code_samples/code_snippets
    video_id = None
    youtube = None
    try:
        youtube = discovery.build('youtube', 'v3', http=creds.authorize(Http()))
    except errors as e:
        print("Error while connecting to YouTube", e)
    finally:
        if youtube is not None:
            if pub_type == 1:
                video_info = get_all_video_info(event_id, pub_type=pub_type, upload_video=True)
                if video_info["you_tube_video_id"] is not None:
                    sys.tracebacklimit = 0
                    raise Exception(("Video with videoID={} already exist " +
                                    "for eventID={}.").format(video_info["you_tube_video_id"], event_id))
                request = youtube.videos().insert(
                    part="snippet,status,recordingDetails",
                    notifySubscribers=notify,
                    body={
                        "recordingDetails": {
                            "recordingDate": video_info['start_time_z']  # ISO 8601 YYYY-MM-DDThh:mm:ss.sZ
                        },
                        "snippet": {
                            "categoryId": "29",  # 29 - Nonprofits & Activism
                            "description": video_info['video_desc'],
                            "title": video_info['video_title'],
                            "tags": video_info['video_tags']
                        },
                        "status": {
                            "privacyStatus": privacy_status,  # private, public or unlisted
                            "publicStatsViewable": True,
                            "license": "youtube",
                            "embeddable": True
                        }
                    },
                    media_body=MediaFileUpload(video_info['video_file'],
                                               filename=video_info['video_file_name'],
                                               mimetype=video_info['mime_type'],
                                               resumable=True))
            else:
                video_info = get_all_video_info(event_id, pub_type=pub_type, upload_video=False)
                if video_info["you_tube_video_id"] is not None:
                    sys.tracebacklimit = 0
                    raise Exception(("Video with videoID={} already exist " +
                                    "for eventID={}.").format(video_info["you_tube_video_id"], event_id))
                request = youtube.videos().insert(
                    part="snippet,status,liveStreamingDetails",
                    notifySubscribers=notify,
                    body={
                        "liveStreamingDetails": {
                            "scheduledStartTime": video_info['start_time_z'],  # ISO 8601 YYYY-MM-DDThh:mm:ss.sZ
                            "scheduledEndTime": video_info['end_time_z']  # ISO 8601 YYYY-MM-DDThh:mm:ss.sZ
                        },
                        "snippet": {
                            "categoryId": "29",  # 29 - Nonprofits & Activism
                            "description": video_info['video_desc'],
                            "title": video_info['video_title'],
                            "tags": video_info['video_tags'],
                            "liveBroadcastContent": video_info['live_status']  # none, upcoming or live
                        },
                        "status": {
                            "privacyStatus": privacy_status,  # private, public or unlisted
                            "publicStatsViewable": True,
                            "license": "youtube",
                            "embeddable": True
                        }
                    })
            response = request.execute()
            print(response)
            if 'id' in response:
                video_id = response['id']
                # print(video_id)
                # Add code to update MediaInfo table
                response = upload_thumbnail(creds, video_id, video_info["thumbnail_file"])
                if not ('items' in response):
                    sys.tracebacklimit = 0
                    raise Exception(("Not able to add thumbnail to videoID={} from " +
                                    "eventID={}.").format(video_info["you_tube_video_id"], event_id))
    return video_id


def upload_thumbnail(creds, video_id, file_path):
    response = None
    youtube = None
    try:
        youtube = discovery.build('youtube', 'v3', http=creds.authorize(Http()))
    except errors as e:
        print("Error while connecting to YouTube", e)
    finally:
        if youtube is not None:
            request = youtube.thumbnails().set(
                videoId=video_id,
                media_body=file_path
            )
            response = request.execute()
    return response


def main():
    scopes = ['https://www.googleapis.com/auth/youtube',
              'https://www.googleapis.com/auth/youtube.force-ssl',
              'https://www.googleapis.com/auth/youtube.upload']
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_id.json', scopes)
        creds = tools.run_flow(flow, store)

    response = add_video(creds, event_id=1319, notify=False, privacy_status="unlisted", pub_type=1)
    print(response)


if __name__ == '__main__':
    main()

# Version 1.0
