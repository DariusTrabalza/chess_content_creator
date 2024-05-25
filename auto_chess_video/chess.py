'''
This script will:
1.scrape data from magnus carlson most recent games
2.take that file and use the chess.com or similar board to play the game.
    -moves will be made on a 3-5 second basis (see what works well)
3.the game will be screen recorded or something to the same effect of getting the video file
4.the file will automatically be uploaded to youtube
5.the titles will be automatically generated and be accurate
6.A thumb nail will automatically be generated for the video
7.the script will check regulary for new games.

additional
-The script will include more top players
-the script can also regulary upload from an archive of famous games
-ai generated commentary of thats happening during the game
-add resignation overlay or draw at the end of match
-could auto add timestamps on youtube somehow
-could ask ai to make cartoon face of oppenents in a anime battle for thumbnails

installs
-selenium
-webdriver-manager


NOTES:
I'm not sure if i can get the pgn games from chess.com or not. maybe i get from somewhere else and play them on chess.com

pick up notes:


-"https://theweekinchess.com/a-year-of-pgn-game-files" This site has most recent tournament results.
    -results come all together
    -calculate how to seperate them intoin dividual files
    -save them to a database with appropriate titles
    -how to i select specific information for the titles?
        -do i search for words
        -or just count the number of square brackets
        -reg ex?
        -do i convert to json?
        -do i make a program that converts the each game into a dict?

-continue to get the most recent games
-create a function that gets games and adds them to a data base
-create a function that takes games from database and play the game through on chess.com as screen records the game
-create a function that logs into youtube account and uploads video of games at correct speed.

-yes i need to use the entire pgn text for the game to work. can i split on [event?]

-tip for getting the dict of titles and games:
    -each file should be the same event each time. 
    -therefore saave the event name
    -then spit on [Event "anything"]
    -and add it in later

-when creating the title call if name the dict already exist add match 2. if still exist add 1 to 2 and try again.

learn about xpaths and how to refer to specific elements of html

-should probably order uploads by round?

-check for sudanames for players?

-if im trying to get the right length of recording i should use the number of moves * seconds of moves plus a buffer.

-do i want to add titles and outro for the videos.

-Do I just want magnus?


-Use pyautogui for the screen recording and everything outside of the browser


-something is happening with the second driver opening chess.com maybe i need new one there?

'''

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


#imports for file opening
import os
import glob

import time
import chess_login



def main():
    
    driver = download_recent_pgn()
    chess_matches = find_most_recent_pgn('C:\\Users\\dariu\\Downloads\\')
    chess_match_dict = format_games(chess_matches)
    recordings =run_and_record(chess_match_dict,driver)
    # generate_thumbnail()
    # post_on_youtube()




def find_most_recent_pgn(directory):
    #file path
    pattern = os.path.join(directory,'*.pgn')
    #get list of files with pgn extension
    files_in_downloads = glob.glob(pattern)

    #check for files
    if files_in_downloads:
        #get file path of most recent pgn file
        most_recent_file = max(files_in_downloads, key= os.path.getmtime)

        #read the file
        with open(most_recent_file, "r") as file:
            return file.read()


def download_recent_pgn():
    #keep window open when done
    options = Options()
    options.add_experimental_option("detach", True)
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
        
    except Exception as e:
        print(f"Driver was not created\nError:\n{e}")
    
    #get the games from the site
    print(".....finding games")
    driver.get("https://theweekinchess.com/a-year-of-pgn-game-files")
    driver.maximize_window()
    #select most recent pgn and download
    download_link = driver.find_element("xpath","//table[@class='calendar-table']/tbody/tr[2]/td[last()]/a")
    download_link.click()
    time.sleep(2)
    return driver

def format_games(chess_matches):

    #get the first line of the string to save as event line
    event =[]
    for letter in chess_matches:
        if letter != "]":
            event.append(letter)
        else:
            break
    event.append("]")

    #This is the event name
    event_joined = "".join(event)

    print(f"Event is called:\n{event_joined}")

    #split into a list containing individual games

    single_games_no_event = chess_matches.split(event_joined)

    single_games_with_event = []

    for game in single_games_no_event:
        single_games_with_event.append(f"{event_joined}{game}")

    single_games_with_event = single_games_with_event[1:]
    # print(f"single games with event:\n{single_games_with_event[0]}")

    #NOTE:now we have a list of the individual games. create a dictionary then loop throught the items of the list generating title then adding title and match to dict.

    #store the games in a dict with a title as key
    game_dict = {}

    for game in single_games_with_event:
        split_lines = game.splitlines()


        white_player = split_lines[4][8:-2]
        black_player = split_lines[5][8:-2]

        white_player_temp = white_player.split(',')
        white_player_ordered = white_player_temp[0].strip() + " " +  white_player_temp[1].strip()

        black_player_temp = black_player.split(',')
        black_player_ordered = black_player_temp[1].strip() + " " + black_player_temp[0].strip()
        i = 1
        title = f"{white_player_ordered} vs {black_player_ordered} "

        #add game + title to dict k = title, v = game
        game_dict[title] = game
    print("Games stored in dicts")
    
    return game_dict


def  run_and_record(game_dict,driver):

    
    #This function will run eachgame on the chess.com board and record and save to a sub folder
    # driver = driver
    print("loading games into simulator")
    try:
        driver.get("https://www.chess.com/")
        driver.maximize_window()
    except Exception as e:
        print(f"web page failed open: \n{e}")
    time.sleep(3)
    #log in
    links = driver.find_elements("xpath","//a[@href]")

    for link in links:
        if "Log In" in link.get_attribute("innerHTML"):
            link.click()
            break

    #complete log in details
    email_input_box = driver.find_element("xpath","//input[@aria-label='Username or Email']")    #("xpath","//input[@id='username']")
    if email_input_box:
        print("email box found")
    time.sleep(3)
    email_input_box.click()
    
    email_input_box.send_keys(chess_login.email)

    pw_input_box = driver.find_element("xpath","//input[@type='password']")
    pw_input_box.click()
    pw_input_box.send_keys(chess_login.password)

    login_confirm = driver.find_element("xpath","//button[@id='login']")
    login_confirm.click()

    #go to game explorer
    driver.get("https://www.chess.com/analysis?tab=analysis")
    
    #for every game in dict
    for title,game in game_dict.items():

        pass
        #click pgn reader
        pgn_box = driver.find_element("xpath","//textarea[@aria-label='Paste one or more PGNs, or drag & drop your PGN file here.']")
        pgn_box.click()

        #paste into paste into pgn reader
        pgn_box.send_keys(game)
        #click add game
        add_game_button = driver.find_element("xpath","//button[contains(@class, 'cc-button-component') and contains(@class, 'cc-button-primary') and @type='button']")
        add_game_button.click()

        #press go to first move
        to_start_button = driver.find_element("xpath","//button[@aria-label='First Move']")
        to_start_button.click()

        #begin screen record

        #press play

        #when game is finished save video file to sub folder

        #give the title of the game as the name of the file


def generate_thumbnail():
    #This function will use a prompt to create an appropriate thumbnail and save to a folder witht the corret title.
    pass



def post_on_youtube(recordings):
    #this function will take the recordings and upload them to youtube at specific time slots or every x time while there are new games.

    #title must be correct

    pass


if __name__ == "__main__":
    main()

