import mysql.connector # Must be at beginning or some other packages may cause problems
from mysql.connector import Error
import os
import re
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess as sp
from math import ceil


import pytz
from google_drive_downloader import GoogleDriveDownloader as Gd
# Get database credentials
sys.path.append(str(Path('.').absolute().parent))
# noinspection PyUnresolvedReferences
from Credentials.get_credentials import get_sys_credentials  # noqa: E402

common_images_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "common_images"))
fonts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fonts"))
templates_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))

temp_file_path = os.path.abspath(os.path.join(os.path.expanduser("~"),
                                              "CoehmsPythonScripts",
                                              "Data",
                                              "YouTube",
                                              "temp"))
other_images_path = os.path.abspath(os.path.join(os.path.expanduser("~"),
                                                 "CoehmsPythonScripts",
                                                 "Data",
                                                 "YouTube",
                                                 "common_images"))


def get_event_info(event_id):
    sql1 = """SELECT `EventGroupID`, `EventTypeID`, `SchedStartDate`, `SchedEndDate`, `SchedTimeZone`, 
    `MainSpeakerName`, `MainSpeakerDescription`, `TalkTheme`, `Location`, `KeywordList`, `Title` 
    FROM `EventInfo` WHERE `CoehmsEventID` = %s"""
    sql2 = """SELECT `YouTubeVideoID`, `DriveFileID` FROM `MediaInfo` WHERE `CoehmsEventID` = %s AND 
    `MediaType` = 'video'"""
    sql3 = """SELECT `DriveFileID` FROM `MediaInfo` WHERE `CoehmsEventID` = %s AND `MediaType` = 'audio'"""
    event_info = {"event_id": None, "group_id": None, "type_id": None, "sched_start": None, "sched_end": None,
                  "sched_time_zone": None, "main_speaker": None, "main_speaker_desc": None, "talk_theme": None,
                  "location": None, "keywords": None, "you_tube_video_id": None, "drive_audio_id": None,
                  "drive_video_id": None}
    db_connection = None
    db_credentials = get_sys_credentials("sys_db_coehms_free")
    try:
        connection_config_dict = {
            'user': db_credentials.username,
            'password': db_credentials.password,
            'host': db_credentials.hostname,
            'port': db_credentials.port,
            'database': db_credentials.def_database,
            'connection_timeout': 120,
            'get_warnings': True,
            'use_pure': False,
            'autocommit': True
        }
        # print(connection_config_dict)
        db_connection = mysql.connector.connect(**connection_config_dict)
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if db_connection is not None:
            cursor = None
            try:
                cursor = db_connection.cursor()
                try:
                    cursor.execute(sql1, (event_id,))
                    record = cursor.fetchone()
                    if cursor.rowcount == 1:
                        event_info["event_id"] = event_id
                        event_info["group_id"] = record[0]
                        event_info["type_id"] = record[1]
                        event_info["sched_start"] = record[2]
                        event_info["sched_end"] = record[3]
                        event_info["sched_time_zone"] = record[4]
                        event_info["main_speaker"] = record[5]
                        event_info["main_speaker_desc"] = record[6]
                        event_info["talk_theme"] = record[7]
                        event_info["location"] = record[8]
                        event_info["keywords"] = record[9]
                except Error as e:
                    print("Error executing Sql: {}\n{}".format(sql1, e))
                finally:
                    pass
                # print(event_info)
                try:
                    cursor.execute(sql2, (event_id,))
                    record = cursor.fetchone()
                    if cursor.rowcount == 1:
                        event_info["you_tube_video_id"] = record[0]
                        event_info["drive_video_id"] = record[1]
                except Error as e:
                    print("Error executing Sql: {}\n{}".format(sql2, e))
                finally:
                    pass
                # print(event_info)
                try:
                    cursor.execute(sql3, (event_id,))
                    record = cursor.fetchone()
                    if cursor.rowcount == 1:
                        event_info["drive_audio_id"] = record[0]
                except Error as e:
                    print("Error executing Sql: {}\n{}".format(sql3, e))
                finally:
                    pass
                # print(event_info)
            except Error as e:
                print("Error opening MySQL's cursor", e)
            finally:
                if cursor is not None:
                    cursor.close()
            db_connection.close()
    return event_info


def compile_video_title(event_info, video_dates):
    # Compile theme for video title
    if len(event_info["talk_theme"]) == 0 or event_info["talk_theme"].lower().strip() in ["eucaristía", "eucaristia"]:
        title_video_theme = ""
    else:
        title_video_theme = " - {}".format(event_info["talk_theme"].title())

    # Compile title according to event type
    if event_info["type_id"] == 1 or event_info["type_id"] == 5:
        video_title = "Asamblea de Oración, Sanación y Liberación - {} {}{}".format(video_dates["day_name_es"],
                                                                                    video_dates["date_str_es"],
                                                                                    title_video_theme)
    elif event_info["type_id"] == 2:
        video_title = "Celebración Eucarística y Oración - {} {}{}".format(video_dates["day_name_es"],
                                                                           video_dates["date_str_es"],
                                                                           title_video_theme)
    elif event_info["type_id"] == 3:
        video_title = "Serenata - {} {}{}".format(video_dates["day_name_es"],
                                                  video_dates["date_str_es"],
                                                  title_video_theme)
    elif event_info["type_id"] == 7:
        video_title = "Celebración de la Palabra y Oración - {} {}{}".format(video_dates["day_name_es"],
                                                                             video_dates["date_str_es"],
                                                                             title_video_theme)
    else:
        video_title = "Actividad Especial - {} {}{}".format(video_dates["day_name_es"],
                                                            video_dates["date_str_es"],
                                                            title_video_theme)
    # Remove extra white space and take care of too long titles
    video_title = " ".join(video_title.split())
    video_title = video_title
    if len(video_title) > 100:
        video_title = re.sub("^(.*\\w)(\\W*)$", "\\1", video_title[0:99]) + "…"
    return video_title


def compile_video_description(event_info, video_dates):
    # Compile video description and its subparts
    if event_info["group_id"] == 1 or event_info["group_id"] == 2:
        meeting_name = "Asamblea Semanal"
        live_schedule = "Horario en Vivo: {} de 8:00 PM - 9:30 PM".format(video_dates["day_name_es"])
    else:
        meeting_name = "Evento Especial"
        live_schedule = "Horario en Vivo: Lunes y Viernes de 8:00 PM - 9:30 PM"
    if len(event_info["talk_theme"]) == 0:
        video_desc_talk_theme = ""
    else:
        event_info["talk_theme"] = event_info["talk_theme"].strip()
        if bool(re.match("^.*[\\w|)]$", event_info["talk_theme"])):
            event_info["talk_theme"] = event_info["talk_theme"] + "."
        video_desc_talk_theme = "\nTema: {}\n".format(event_info["talk_theme"])

    if len(event_info["main_speaker_desc"]) == 0:
        video_desc_speaker_details = ""
    else:
        event_info["main_speaker_desc"] = event_info["main_speaker_desc"].strip()
        if bool(re.match("^.*[\\w|)]$", event_info["main_speaker_desc"])):
            event_info["main_speaker_desc"] = event_info["main_speaker_desc"] + "."
        video_desc_speaker_details = "{}\n".format(event_info["main_speaker_desc"])
    if len(event_info["location"]) == 0:
        video_desc_location = ""
    else:
        event_info["location"] = event_info["location"].strip()
        video_desc_location = "Lugar: {}\n".format(event_info["location"])

    video_desc = open('template_video_description.txt', 'r').read().format(meeting_name,
                                                                           video_desc_talk_theme,
                                                                           event_info["main_speaker"],
                                                                           video_desc_speaker_details,
                                                                           live_schedule,
                                                                           video_desc_location)
    video_desc += open('video_description_links.txt', 'r').read()

    return video_desc


def get_all_video_info(event_id, pub_type=1, upload_video=False):
    video_file = None
    mime_type = None
    video_file_name = None

    # Get event info from db
    event_info = get_event_info(event_id)
    if event_info["main_speaker"] is None:
        event_info["main_speaker"] = ""
    if event_info["main_speaker_desc"] is None:
        event_info["main_speaker_desc"] = ""
    if event_info["talk_theme"] is None:
        event_info["talk_theme"] = ""
    if event_info["location"] is None:
        event_info["location"] = ""
    if event_info["keywords"] is None:
        event_info["keywords"] = ""

    video_dates = get_video_dates(event_info["sched_start"], event_info["sched_end"], event_info["sched_time_zone"])
    video_title = compile_video_title(event_info, video_dates)
    video_desc = compile_video_description(event_info, video_dates)

    if event_info["keywords"] == '':
        video_tags = None
    else:
        video_tags = event_info["keywords"].split(",")

    # Compile a custom video thumbnail for the event
    thumbnail_file = compile_custom_thumbnail(event_info)

    # Get video file if needed
    if pub_type == 1 and upload_video:
        video_file_name = get_video_file(event_info, upload_video=upload_video)
        if video_file_name is not None:
            video_file = os.path.join(temp_file_path, video_file_name)
        mime_type = "video/mp4"

    if pub_type == 2:
        live_status = "upcoming"
    elif pub_type == 3:
        live_status = "live"
    else:
        live_status = "none"

    return {"video_file": video_file,
            "mime_type": mime_type,
            "video_file_name": video_file_name,
            "video_title": video_title,
            "video_desc": video_desc,
            "video_tags": video_tags,
            "thumbnail_file": thumbnail_file,
            "live_status": live_status,
            "start_time_z": video_dates["video_date_time_start_z_str"],
            "end_time_z": video_dates["video_date_time_end_z_str"],
            "you_tube_video_id": event_info["you_tube_video_id"],
            "drive_audio_id": event_info["drive_audio_id"],
            "drive_video_id": event_info["drive_video_id"]
            }


def get_video_dates(date_time_start_local, date_time_end_local, time_zone='America/Santo_Domingo'):
    local_tz = pytz.timezone(time_zone)
    zulu_tz = pytz.timezone("Zulu")
    days_of_week = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves",
                    "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
    date_str_es = date_time_start_local.strftime("%d/%m/%Y")
    day_name_es = days_of_week[date_time_start_local.strftime("%A")]
    start_time_str = date_time_start_local.strftime("%I:%M %p")
    end_time_str = date_time_end_local.strftime("%I:%M %p")
    video_date_time_start_z = local_tz.localize(date_time_start_local).astimezone(zulu_tz)
    video_date_time_end_z = local_tz.localize(date_time_end_local).astimezone(zulu_tz)
    video_date_time_start_z_str = video_date_time_start_z.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    video_date_time_end_z_str = video_date_time_end_z.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return {"date_str_es": date_str_es, "day_name_es": day_name_es,
            "start_time_str": start_time_str, "end_time_str": end_time_str,
            "video_date_time_start_z": video_date_time_start_z,
            "video_date_time_end_z": video_date_time_end_z,
            "video_date_time_start_z_str": video_date_time_start_z_str,
            "video_date_time_end_z_str": video_date_time_end_z_str}


def get_video_file(event_info, upload_video=False):
    video_file_name = None
    if event_info["drive_audio_id"] is not None and event_info["drive_audio_id"] > "":
        video_file_name = "VE" + event_info["sched_start"].strftime("%y%m%d%H%M") + ".mp4"
    elif event_info["drive_audio_id"] is None:
        video_file_name = "VO" + event_info["sched_start"].strftime("%y%m%d%H%M") + ".mp4"

    if video_file_name is not None and video_file_name > "":
        if upload_video and not os.path.isfile(os.path.join(temp_file_path, video_file_name)):
            video_file_name = compile_mp4_video_from_audio(event_info)
            if video_file_name is None:
                sys.tracebacklimit = 0
                raise Exception("No able to compile video for eventID={}.".format(event_info["event_id"]))
    return video_file_name


def compile_custom_thumbnail(event_info):
    # event_info["type_id"] = 6
    theme_text = event_info["talk_theme"]
    # theme_text = "ABCDEFG HIJKLM NOPQRS TUVWXYZ ABCDEFG"
    # theme_text = "ABCDEFG HIJKLM NOPQRS TUVWXYZ ABCDEFG HIJKLM"
    # theme_text = "ABCDEFG HIJKLM NOPQRS TUVWXYZ ABCDEFG HIJKLM NOPQRS TUVWXYZ"
    # theme_text = "ABCDEFGHIJKLM NOPQRSTUVWXYZ ABCDEFGHIJKLM NOPQRSTUVWXYZ"
    theme_text = theme_text.replace("\"", "'")
    print("Event ID: {}".format(event_info["event_id"]))
    print("Event Theme: {}".format(theme_text))

    if event_info["type_id"] == 1 or event_info["type_id"] == 3 or event_info["type_id"] == 5:
        template_name = "asamblea_thumbnail"
    elif event_info["type_id"] == 2 or event_info["type_id"] == 7:
        template_name = "eucaristia_thumbnail"
    else:
        template_name = "otros_thumbnail"
    print("Template Name: {}.tex".format(template_name))

    thumbnail_file = os.path.join(templates_path, "thumbnails", "{}_id_{}.png".format(template_name,
                                                                                      event_info["event_id"]))
    if theme_text != "" and os.path.exists(os.path.join(templates_path, "thumbnails", "{}.tex".format(template_name))):
        commands = "cd {};".format(os.path.join(templates_path, "thumbnails"))
        commands += "sh tex_to_png.sh \"{}\" \"{}\" \"{}\";".format(template_name,
                                                                    event_info["event_id"],
                                                                    theme_text)
        result = os.system(commands)
        if not (result == 0 and os.path.isfile(thumbnail_file)):
            thumbnail_file = None
    else:
        commands = "cd {};".format(os.path.join(common_images_path, "thumbnails"))
        commands += "cp {}_1.png {};".format(template_name, thumbnail_file)
        result = os.system(commands)
        if not (result == 0 and os.path.isfile(thumbnail_file)):
            thumbnail_file = None
    print("Commands: {}".format(commands))
    # Move file to temp dir
    if thumbnail_file is not None:
        current_location = thumbnail_file
        thumbnail_file = os.path.join(temp_file_path, "custom_thumbnail_{}.png".format(event_info["event_id"]))
        os.rename(current_location, thumbnail_file)
    return thumbnail_file


def compile_mp4_video_from_audio(event_info):
    file_name = None
    if event_info["drive_audio_id"] is not None and event_info["drive_audio_id"] > "":
        audio_dest = os.path.join(temp_file_path, "AE" + event_info["sched_start"].strftime("%y%m%d%H%M") + ".mp3")
        Gd.download_file_from_google_drive(file_id=event_info["drive_audio_id"],
                                           dest_path=audio_dest, overwrite=True, showsize=False)
        if os.path.isfile(audio_dest):
            print("Source Audio: {}".format(audio_dest))
            # Create thumbnail if not available
            thumbnail_dest = os.path.join(temp_file_path, "custom_thumbnail_{}.png".format(event_info["event_id"]))
            if not os.path.isfile(thumbnail_dest):
                compile_custom_thumbnail(event_info)
            if os.path.isfile(thumbnail_dest):
                # Select video source based on EventTypeId
                if event_info["type_id"] in [1, 3, 5]:
                    scenes = os.path.join(other_images_path, "escenas_asamblea.mp4")
                elif event_info["type_id"] in [2, 7]:
                    scenes = os.path.join(other_images_path, "escenas_eucaristia.mp4")
                else:
                    scenes = os.path.join(other_images_path, "escenas_asamblea.mp4")
                if os.path.isfile(scenes):
                    print("Source Video: {}".format(scenes))

                    first_scene_dest = os.path.join(temp_file_path, "first_scene_{}.mp4".format(event_info["event_id"]))




                    #if result == 0 and os.path.isfile(first_scene_dest):

                    scenes_list_dest = os.path.join(temp_file_path, "scenes_list_{}.txt".format(event_info["event_id"]))
                    list_file = open(scenes_list_dest, "w")
                    list_file.write("file '{}'\n".format(first_scene_dest))
                    list_file.write("file '{}'\n".format(scenes))
                    list_file.close()
                    temp_video_file_name = "VE" + event_info["sched_start"].strftime("%y%m%d%H%M") + "_temp.mp4"
                    temp_video_dest = os.path.join(temp_file_path, temp_video_file_name)
                    result = os.system("ffmpeg -f concat -safe 0 -i " + scenes_list_dest + " -c copy -y " +
                                       temp_video_dest)
                    if result == 0 and os.path.isfile(temp_video_dest):
                        video_file_name = "VE" + event_info["sched_start"].strftime("%y%m%d%H%M") + ".mp4"
                        video_dest = os.path.join(temp_file_path, video_file_name)
                        result = os.system("ffmpeg -y -i " + temp_video_dest + " -i " + audio_dest +
                                           " -map 0:v:0 -map 1:a:0 -c copy -shortest " + video_dest)
                        if result == 0 and os.path.isfile(video_dest):
                            print("Output Video: {}".format(video_dest))
                            file_name = video_file_name
                            os.system("rm " + audio_dest)
                            os.system("rm " + scenes_list_dest)
                            os.system("rm " + temp_video_dest)
    return file_name


def png_to_mp4(png_source, mp4_duration=60, mp4_dest=None, video_fps=20, video_scale="1280:720", crf=25, rate="1500k",
               max_rate="1500k", buffer_size="4500k", encoder_options=None, fade_in_frames=None, fade_out_frames=None,
               fade_background="black"):
    if os.path.isfile(png_source) and mp4_dest is not None and mp4_duration > 0 and video_fps > 0:
        filter_text = "fps={},scale={}".format(video_fps, video_scale)
        if fade_in_frames is None:
            fade_in_frames = 0
        if fade_in_frames > 0:
            filter_text += ",fade=t=in:s=0:n={}:c={}".format(fade_in_frames, fade_background)
        if fade_out_frames is None:
            fade_out_frames = 0
        if fade_out_frames > 0:
            out_start_frame = mp4_duration * video_fps - fade_out_frames
            filter_text += ",fade=t=out:s={}:n={}:c={}".format(out_start_frame, fade_out_frames, fade_background)
        # print(filter_text)
        if crf is None:
            crf = 0
        if crf > 0:
            quality_option = " -crf {}".format(crf)
        else:
            quality_option = " -b:v {}".format(rate)
        if encoder_options is None:
            encoder_options = ""
        if encoder_options > "":
            encoder_options = " -x264opts \"{}\"".format(encoder_options)
        command = ("ffmpeg -loop 1 -i \"{}\" -c:v libx264 -preset veryslow{} -maxrate {} -bufsize {} -t {}{} " +
                   "-filter_complex \"{}\" -pix_fmt yuv420p -y \"{}\" && " +
                   "echo \"Encoding Completed\"").format(png_source, quality_option, max_rate, buffer_size,
                                                         mp4_duration, encoder_options, filter_text, mp4_dest)
        print(command)
        result = os.system(command)
        if not (result == 0 and os.path.isfile(mp4_dest)):
            mp4_dest = None
    return mp4_dest


def concat_mp4(source_list, mp4_dest=None):
    if type(source_list) is list and len(source_list) > 1 and mp4_dest is not None:
        with TemporaryDirectory() as temp_dir:
            files_list_dest = os.path.join(temp_dir, "list.txt")
            files_list = open(files_list_dest, "w")
            for f in source_list:
                files_list.write("file '{}'\n".format(f))
            files_list.close()
            command = ("ffmpeg -f concat -safe 0 -i \"{}\" -c copy -y \"{}\" && " +
                       "echo \"Concat Completed\"").format(files_list_dest, mp4_dest)
            print(command)
            result = os.system(command)
            if not (result == 0 and os.path.isfile(mp4_dest)):
                mp4_dest = None
    else:
        mp4_dest = None
    return mp4_dest


def media_probe(media_dest):
    if not os.path.isfile(media_dest):
        raise Exception('Give ffprobe a full file path of the video')

    command = ["ffprobe", "-loglevel", "quiet", "-print_format", "json",
               "-show_format", "-show_streams", media_dest]

    pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT)
    out, err = pipe.communicate()
    return json.loads(out)


def media_duration(media_dest):
    media_info = media_probe(media_dest)
    # print(media_info)
    if 'format' in media_info:
        if 'duration' in media_info['format']:
            return float(media_info['format']['duration'])

    if 'streams' in media_info:
        # commonly stream 0 is the video
        for s in media_info['streams']:
            if 'duration' in s:
                return float(s['duration'])
    raise Exception('No duration found')


def replicate_mp4(mp4_source, target_duration=None, output_dest=None):
    if target_duration is None:
        target_duration = 0
    if os.path.isfile(mp4_source) and target_duration > 0 and output_dest is not None:
        source_duration = media_duration(mp4_source)
        print("Source Duration: ".format(source_duration))
        rep_amount = ceil(target_duration / source_duration)
        print(rep_amount)
        source_list = []
        for i in range(rep_amount):
            source_list.append(mp4_source)
        print(source_list)
        output_dest = concat_mp4(source_list, output_dest)
    else:
        output_dest = None
    return output_dest
