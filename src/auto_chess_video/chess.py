
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
import requests
from openai import OpenAI


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
    run_and_record(chess_match_dict,driver)
    generate_thumbnail(chess_match_dict)
    post_on_youtube(driver)


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
    os.environ['WDM_ARCH'] = 'x64'
    #keep window open when done
    options = Options()
    options.add_experimental_option("detach", True)
    ###
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    ###
    chrome_driver_path = chess_login.chromedriver_path
    print(chrome_driver_path)
    try:
        driver = webdriver.Chrome(service=Service(chrome_driver_path),options=options)
        
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
        print(game)
        split_lines = game.splitlines()
        white_player = split_lines[4][8:-2]
        black_player = split_lines[5][8:-2]
        white_player_temp = white_player.split(',')
        print(white_player_temp)
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
    
    #for every game in dict
    for title,game in game_dict.items():
        #go to game explorer
        driver.get("https://www.chess.com/analysis?tab=analysis")
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
        title_formatted = title.strip().replace(' ','_' )


        try:
            result = subprocess.run([bash_path,'./record.sh', length_of_recording,title_formatted],capture_output=True, text=True, check=True)
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
        print(f"finished {title}")
        

def generate_thumbnail(game_dict):
    #for every match generate a thumbnail    
    for title,game in game_dict.items():
        #connect to openAI 
        client = OpenAI(api_key = chess_login.openai_key)
        response = client.images.generate(
        model="dall-e-3",
        prompt="using current trends of top performing youtube thumbnail colours and compositions, create a thumbnail for a in intense chess battle in the style of interesting 20th century artists. Do not feature any people in this image, also no writing should be in the image",
        size="1024x1024",
        quality="standard",
        #num of images
        n=1,
        )
        #store response
        image_url = response.data[0].url
        
        try:
            #Send a GET request to the URL
            response = requests.get(image_url)
        except Exception as e:
            print(e)

        #Check if the request was successful
        if response.status_code == 200:
            image_path = os.path.join("thumbnails", f"{title}.png")
            # Save the image to the current directory with the specified filename
            with open(image_path, "wb") as file:
                file.write(response.content)
            print(f"{title} image saved successfully!")
        else:
            print(f"Failed to retrieve the image for {title}. Status code:{response.status_code}")
            


def post_on_youtube(driver):
    #this function will take the recordings and upload them to youtube at specific time slots or every x time while there are new games.
    #go to youtube studio.com
    driver.get("https://studio.youtube.com/")

    # try:
       
    #     accept_terms_button =driver.find_element("xpath","//*[@id='yDmH0d']/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/form[2]/div/div/button/span")
    #     accept_terms_button.click()
    # except Exception as e:
    #     print(e)

    #log in
    # sign_in_button =driver.find_element("xpath","//*[@id='topbar']/div[2]/div[2]/ytd-button-renderer/yt-button-shape/a/yt-touch-feedback-shape/div/div[2]")
    # sign_in_button.click()

    email_box = driver.find_element("xpath","//*[@id='identifierId']")
    email_box.send_keys(chess_login.youtube_email)

    next_button =driver.find_element("xpath","//*[@id='identifierNext']/div/button/span")
    next_button.click()

    time.sleep(5)
    youtube_password = driver.find_element("xpath", "//input[@type='password']")
    print("element found")
    print(youtube_password)
    youtube_password.send_keys(chess_login.youtube_password)
    print('password complete')

    next_button =driver.find_element("xpath","//*[@id='passwordNext']/div/button/span")
    next_button.click()

    time.sleep(5)
    chess_account = driver.find_element("xpath","//yt-formatted-string[text()='No Time For Chess']")
    chess_account.click()   


    #select upload video

    #find the video

    #title should be done

    #Enter a description

    #upload thumbnail

    #click next

    #click next again


    #click next again


    #click public

    #click publish
    pass


if __name__ == "__main__":
    main()

