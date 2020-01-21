import sys
from googleapiclient import discovery, errors
from httplib2 import Http
from oauth2client import file, client, tools
from you_tube_common import get_all_video_info
from you_tube_add_video import upload_thumbnail


def update_video(creds, event_id, privacy_status="public", pub_type=1):
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
                video_info = get_all_video_info(event_id, pub_type=pub_type, upload_video=False)
                if video_info["you_tube_video_id"] is None:
                    sys.tracebacklimit = 0
                    raise Exception(("No video_id exist for eventID=" +
                                     "{}.").format(event_id))
                request = youtube.videos().update(
                    part="snippet,status,recordingDetails",
                    body={
                        "id": video_info["you_tube_video_id"],
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
                    })
            else:
                video_info = get_all_video_info(event_id, pub_type=pub_type, upload_video=False)
                if video_info["you_tube_video_id"] is None:
                    sys.tracebacklimit = 0
                    raise Exception(("No video_id exist for eventID=" +
                                     "{}.").format(event_id))
                request = youtube.videos().update(
                    part="snippet,status,liveStreamingDetails",
                    body={
                        "id": video_info["you_tube_video_id"],
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
                response = upload_thumbnail(creds, video_id, video_info["thumbnail_file"])
                # print(response)
                if not ('items' in response):
                    sys.tracebacklimit = 0
                    raise Exception(("Not able to add thumbnail to videoID={} from " +
                                     "eventID={}.").format(video_info["you_tube_video_id"], event_id))
    return video_id


def main():
    scopes = ['https://www.googleapis.com/auth/youtube',
              'https://www.googleapis.com/auth/youtube.force-ssl',
              'https://www.googleapis.com/auth/youtube.upload']
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_id.json', scopes)
        creds = tools.run_flow(flow, store)
    response = update_video(creds, event_id=1319, privacy_status="unlisted", pub_type=1)
    print(response)


if __name__ == '__main__':
    main()

# Version 1.0
