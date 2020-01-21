import os

from you_tube_common import common_images_path, temp_file_path, png_to_mp4, concat_mp4


def main():
    duration = 10
    fsb = 10
    crf = 25  # 25 Works
    rate = "350k"  # 350K Works
    max_rate = "350k"  # 350K Works
    buffer = "1750k"  # 1750K Works
    encoder_opts = None
    f_in = 3  # 3 and 12 Works
    f_out = 3  # 3 and 12 Works
    color = "black"  # black Works
    trans_units = 0  # 0 Works
    trans_decimals = 75  # 75 Works
    if trans_units is None or trans_decimals is None:
        background = color
    else:
        background = "{}@{}.{}".format(color, trans_units, trans_decimals)
    png_source = os.path.join(common_images_path, "thumbnails", "asamblea_thumbnail_1.png")
    mp4_dest1 = os.path.join(temp_file_path, "out1.mp4")
    mp4_file = png_to_mp4(png_source, mp4_duration=duration, mp4_dest=mp4_dest1, video_fps=fsb, crf=crf,
                          rate=rate, max_rate=max_rate, buffer_size=buffer, encoder_options=encoder_opts,
                          fade_in_frames=f_in, fade_out_frames=f_out, fade_background=background)

    print(mp4_file)
    out_mp4_dest = os.path.join(temp_file_path,
                                ("output_{}fsb_{}crf_{}rate_{}maxrate_{}buf" +
                                 "_{}in_{}out_{}color_{}_{}trans.mp4").format(fsb, crf, rate, max_rate, buffer, f_in,
                                                                              f_out, color, trans_units,
                                                                              trans_decimals))
    mp4_file = concat_mp4([mp4_dest1, mp4_dest1, mp4_dest1, mp4_dest1, mp4_dest1], mp4_dest=out_mp4_dest)
    if os.path.exists(mp4_dest1):
        os.remove(mp4_dest1)
    print(mp4_file)


if __name__ == '__main__':
    main()

# Version 1.0
