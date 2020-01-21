import os

from you_tube_common import png_to_mp4, common_images_path, temp_file_path


def main():
    # png_name = "eucaristia_thumbnail_1"
    png_name = "scene_08"
    #duration = 10
    duration = 90
    fsb = 10
    crf = 25  # 25 Works
    rate = "350k"  # 350K Works
    max_rate = "350k"  # 350K Works
    buffer = "1750k"  # 1750K Works
    encoder_opts = None
    # encoder_opts = "bframes=3"
    # encoder_opts = "ref=4"
    f_in = 3  # 3 and 12 Works
    f_out = 3  # 3 and 12 Works
    color = "black"  # black Works
    trans_units = 0  # 0 Works
    trans_decimals = 75  # 75 Works
    if trans_units is None or trans_decimals is None:
        background = color
    else:
        background = "{}@{}.{}".format(color, trans_units, trans_decimals)
    png_source = os.path.join(common_images_path, "scenes_eucaristia", "{}.png".format(png_name))

    out_mp4_dest = os.path.join(temp_file_path, "{}.mp4".format(png_name))
    # out_mp4_dest = os.path.join(temp_file_path,
    #                             ("output_{}fsb_{}crf_{}rate_{}maxrate_{}buf" +
    #                              "_{}in_{}out_{}color_{}_{}trans.mp4").format(fsb, crf, rate, max_rate, buffer, f_in,
    #                                                                           f_out, color, trans_units,
    #                                                                           trans_decimals))

    mp4_file = png_to_mp4(png_source, mp4_duration=duration, mp4_dest=out_mp4_dest, video_fps=fsb, crf=crf,
                          rate=rate, max_rate=max_rate, buffer_size=buffer, encoder_options=encoder_opts,
                          fade_in_frames=f_in, fade_out_frames=f_out, fade_background=background)
    print(mp4_file)


if __name__ == '__main__':
    main()

# Version 1.0
