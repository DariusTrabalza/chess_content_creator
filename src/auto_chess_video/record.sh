#!/bin/bash

set=eu

record_time=$1

echo "Starting Video Recording"
ffmpeg -f gdigrab -framerate 60 -offset_x 360 -offset_y 150 -video_size 811x877 -i desktop -f dshow -i audio="Microphone (Realtek(R) Audio)" -t "$record_time" ./recorded_match.mp4 > ffmpeg_output.log 2>&1 &

# Save the PID of the background process
echo $! > ./ffmpeg_pid.txt
