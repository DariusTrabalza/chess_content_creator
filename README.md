# Project Overview
This project is designed to create visual content of top chess games. It will get top games from recent contests and simulate the game using a scraped PGN file. This will then be virtually played on the on chess.com simulator and will be recorded. The game will be played with a custom interval between moves. Depending on what the user wants. This will enable the user to see very long games more quickly and extremely quick games more slowly. Resulting in the oppurtunity to learn from the masters at a pace that suits them.


# Prerequisites
install ffmpeg from https://ffmpeg.org/download.html
note:
You may need to add path in by : Advanced System Settings > System Properties > Environment Variables > click path > click edit > add in pathway to ffmpeg\bin
Create a folder in the same directory called 'thumbnails'.

Python 3.8 or higher
Required Python packages:
subprocesses
logging
os
glob
time
selenium
openai
webdriver-manager