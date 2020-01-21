#!/bin/bash

# Calling Example: sh repeat_mp4.sh "all_scenes" "17"

FileName=$1
RepeatTimes=$2

rm -f repeat_list.txt
for i in `seq 1 $RepeatTimes`; do echo "file '${FileName}.mp4'" >> repeat_list.txt; done
ffmpeg -f concat -safe 0 -i repeat_list.txt -c copy -y "${FileName}_x_${RepeatTimes}.mp4"
rm -f repeat_list.txt
rm -f "${FileName}.mp4"

