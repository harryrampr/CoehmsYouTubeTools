import os
from tempfile import TemporaryDirectory
import numpy as np

from you_tube_common import common_images_path, temp_file_path, png_to_mp4, concat_mp4, replicate_mp4, \
    other_images_path


def main():
    all_scenes_duration = (0 * 3600) + (2 * 60) + (0 * 1)  # in seconds
    all_scenes_dest = os.path.join(other_images_path, "asamblea_scenes_new.mp4")
    images_list = [os.path.join(common_images_path, "thumbnails", "asamblea_thumbnail_2.png"),
                   os.path.join(common_images_path, "thumbnails", "asamblea_thumbnail_1.png"),
                   os.path.join(common_images_path, "thumbnails", "asamblea_thumbnail_2.png"),
                   os.path.join(common_images_path, "thumbnails", "asamblea_thumbnail_1.png"),
                   os.path.join(common_images_path, "thumbnails", "asamblea_thumbnail_2.png"),
                   os.path.join(common_images_path, "thumbnails", "asamblea_thumbnail_1.png")]

    if type(images_list) is list and len(images_list) > 1 and all_scenes_duration > 0:
        with TemporaryDirectory() as temp_dir:
            unique_images = np.unique(np.array(images_list).tolist())
            unique_scenes = {}
            for index, png in enumerate(unique_images):
                print(index, png)
                png_mp4_dest = os.path.join(temp_dir, "out{}.mp4".format(index))
                print(png_mp4_dest)
                mp4_file = png_to_mp4(png, mp4_duration=90, mp4_dest=png_mp4_dest, video_fps=10, crf=25,
                                      rate="350k", max_rate="350k", buffer_size="1750k", encoder_options=None,
                                      fade_in_frames=3, fade_out_frames=3, fade_background="black@0.75")
                print(mp4_file)
                if mp4_file is None:
                    raise Exception('Invalid png_to_mp4 parameters')
                unique_scenes[png] = mp4_file
            print(unique_scenes)
            #scenes_dict = dict()


            mp4_lists = images_list

            return

            out1_mp4_dest = os.path.join(temp_dir, "output_1.mp4")
            mp4_file = concat_mp4([mp4_dest1, mp4_dest1, mp4_dest1, mp4_dest1, mp4_dest1], mp4_dest=out1_mp4_dest)
            print(mp4_file)

            mp4_file = replicate_mp4(out1_mp4_dest, target_duration=all_scenes_duration, output_dest=all_scenes_dest)
            print(mp4_file)
    else:
        raise Exception('Invalid main parameters')


if __name__ == '__main__':
    main()

# Version 1.0
