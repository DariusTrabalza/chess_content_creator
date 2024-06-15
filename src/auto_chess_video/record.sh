#!/bin/bash

set=eu

record_time=$1

gdigrab -framerate 60 -offset_x 360 -offset_y 150 -video_size 811x877 -i desktop -f dshow -i audio="Microphone (Realtek(R) Audio)" -t $record_time recorded_match.mp4 &
