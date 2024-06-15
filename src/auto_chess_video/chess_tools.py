import pyautogui
import time



def find_co_ordinates():
    try:
        while True:
            # Get the current mouse coordinates
            x, y = pyautogui.position()
            
            # Print the coordinates
            print(f"X: {x}, Y: {y}", end='\r', flush=True)
            
            # Pause for a short period to reduce CPU usage
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nScript terminated.")