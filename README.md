# Project Overview
This project is designed to create visual content of top chess games. It will get top games from recent contests and simulate the game using a scraped PGN file. This will then be virtually played in the on chess.com and be recorded. The game will be played with a custom interval between moves. Depending on what the user wants. This will enable us to see very long games more quickly and extremely quick games more slowly. Making it easier to do analysis.


# Prerequisites
install ffmpeg from https://ffmpeg.org/download.html
note:
You may need to add path in by : Advanced System Settings > System Properties > Environment Variables > click path > click edit > add in pathway to ffmpeg\bin

Python 3.8 or higher
Required Python packages:
subprocesses
logging
os
glob
time
selenium