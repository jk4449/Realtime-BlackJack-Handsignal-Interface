import numpy as np
import cv2 as cv
from random import shuffle
import time
import utils
import game
import user_input

if __name__ == "__main__":
    # take picture of key gestures --------------------------------------------------------------------------------
    key_gesture_name = ["doubledown", "split"]
    my_grs = user_input.GRS()
    key_gestures = my_grs.initialize_key_gestures(key_gesture_name)

    # gameplay --------------------------------------------------------------------------------
    for i in range(15):
        thisgame = game.Game([[],[]], [], [])
        #player's turn
        scores, deck = thisgame.player_round(my_grs)
        if sum(scores) > 0: # if there is any unbusted playable set left
            #dealer's turn
            dealer_score = thisgame.dealer_round()
            for s in range(len(scores)):
                if scores[s] > dealer_score:
                    thisgame.display("Player" + str(s+1) + " WIN!", 2)
                else:
                    thisgame.display("Player" + str(s+1) + " LOOSE", 2)
        thisgame.display("end of round", 1)
    thisgame.display("Good game. I hope to play with you again.")
