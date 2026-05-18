#!/usr/bin/env bash

# gource --auto-skip-seconds 0.1 -s 0.1 --output-ppm-stream - |   \
#     ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - -c:v libx264 \
#     -preset fast -crf 18 -pix_fmt yuv420p -movflags +faststart Visualized_Git_History.mp4


gource --auto-skip-seconds 0.1 -s 0.1 --title "Daker" -f