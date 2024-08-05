
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import subprocess
from helper_functions import count_moves,seconds_to_timestamp
import logging
import os


#imports for file opening
import os
import glob

import time
import chess_login

#set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
        title = f"{white_player_ordered} vs {black_player_ordered} "
        #add game + title to dict k = title, v = game
        game_dict[title] = game
    print("Games stored in dicts")
    
    return game_dict

def  run_and_record(game_dict,driver):
    #This function will run eachgame on the chess.com board and record and save to a sub folder
    print("Opening chess.com")
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
        #click pgn reader 
        pgn_box = driver.find_element("xpath","//*[@id='board-layout-sidebar']/div/div/div[1]/div/div[2]/div[7]/div/div/textarea")
        pgn_box.click()
        #paste into paste into pgn reader
        pgn_box.send_keys(game)
        #click add game
        add_game_button = driver.find_element("xpath","//button[contains(@class, 'cc-button-component') and contains(@class, 'cc-button-primary') and @type='button']")
        add_game_button.click()
        #press go to first move
        to_start_button = driver.find_element("xpath","//button[@aria-label='First Move']")
        to_start_button.click()

        #calculate number of moves in the game
        number_of_moves = int(count_moves(game)) * 2
        print(f"Number of moves calculated: {number_of_moves}")

        #slowdown rate (Initial rate is 1 second per move) 
        slowdown_rate = 1 
        num_moves_with_buffer = (int(number_of_moves) * slowdown_rate) + 20
        print(f"Number of moves with buffer: {num_moves_with_buffer}")

        #convert to time
        length_of_recording = seconds_to_timestamp(num_moves_with_buffer)
        print(f"Length of recording: {length_of_recording}")
        logger.info("getting record.sh file path")

        #check file path of record.sh
        script_path = os.path.join(os.getcwd(), 'record.sh').replace('\\', '/')
        print(f"record.sh path: {script_path}")

        logger.info('Attempting recording')
        #start recording
        bash_path =r'C:\Program Files\Git\usr\bin\bash.exe'
        try:
            result = subprocess.run([bash_path,'./record.sh', length_of_recording],capture_output=True, text=True, check=True)
            print(result.stdout)
            print(result.stderr)

        except FileNotFoundError:
            print("Unable to locate record.sh")

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the script: {e}")
            print(e.stdout)
            print(e.stderr)

        #press next move and wait x seconds
        logger.info("Beginning game moves")
        next_move_button = driver.find_element("xpath","/html/body/div[4]/div/div/div[3]/div[1]/button[4]/span")
        for _ in range(int(number_of_moves)):
            next_move_button.click()
            time.sleep(slowdown_rate)
        logger.info("All moves complete")
        #when game is finished save video file to sub folder

        #give the title of the game as the name of the file
        print("finished")
        return "end of game"

def generate_thumbnail():
    #This function will use a prompt to create an appropriate thumbnail and save to a folder witht the corret title.
    pass


def post_on_youtube(recordings):
    #this function will take the recordings and upload them to youtube at specific time slots or every x time while there are new games.

    #title must be correct
    pass


if __name__ == "__main__":
    main()

