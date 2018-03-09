#!/bin/bash

# converts all mp3s in a directory to 16khz 16bit mono wavs compatible with
# many speech recognition software

for file in ./*.mp3
do
    ffmpeg - i "$file" -acodec pcm_s16le -ac 1 -ar 16000 "${file[@]/%mp3/wav}"
done
