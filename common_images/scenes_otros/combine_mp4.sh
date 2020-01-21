#!/bin/bash

# Calling Example: sh combine_mp4.sh

rm -f scenes_list.txt
for f in scene_*.mp4; do echo "file '$f'" >> scenes_list.txt; done
ffmpeg -f concat -safe 0 -i scenes_list.txt -c copy -y all_scenes.mp4
rm -f scenes_list.txt
# rm -f scene_*.mp4

