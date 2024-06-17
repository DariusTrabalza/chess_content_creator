
import time

#this function gets the number of moves of each game
def count_moves(match):
    number_of_moves = []
    #reverse pgn file
    reversed_match = match[::-1]
    #for each character of the pgn
    counter = 0
    #for each character in thepgn
    for character in reversed_match:
        # print(f"counter: {counter} char: {character}")
        #if that character is a full stop
        if character == ".":
            #append the next 3 characters
            for i in range(1,4):
                number_of_moves.append(reversed_match[counter + i])
             #remove non numeric characters and reverse   
            number_of_moves = [num for num in number_of_moves if num.isnumeric()][::-1]
            #join the list of digits together
            number_of_moves = ''.join(number_of_moves)
            break
            #append numbers before it to number_of _moves
        else:
            counter += 1


    return(number_of_moves)


#this function converts seconds to timestamp
def seconds_to_timestamp(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(int(seconds)))

    



count_moves("hello there . 23423 .  41e23r gwthere  wgserlasy number is 221. qb4qerg trehre 22 1-0")
