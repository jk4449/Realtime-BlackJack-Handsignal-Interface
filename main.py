import numpy as np
import cv2 as cv
from random import shuffle
import time

#BlackJack helper function & class ------------------------------------------------------------------
def card_to_image(card):
    img_name = card[0] + "_" + card[1] + ".png"
    img = cv.imread("PlayingCards/" + img_name, cv.IMREAD_COLOR)
    return img

def card_to_string(card):
    return str(card[1]) + " of " + str(card[0])

def calculate_score(cards):
    score = 0
    num_of_A = 0
    for card in cards:
        if card == ["blank", "card"]:
            score += 0
        elif card[1] == "ace":
            score += 1
            num_of_A += 1
        elif card[1] == "king" or card[1] == "queen" or card[1] == "jack":
            score += 10
        else:
            score += int(card[1])
    if num_of_A > 0 and score <= 11:
        score += 10
    return score

class Game:
    def __init__(self, p_cards=[[],[]], d_cards=[], deck=[]): #empty list if you wanna start fresh.
        # new deck
        self.dealer_card_show = False
        self.num_of_player = 1
        self.curr_player = 0
        numbers = ["ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king"]
        suits = ["hearts", "clubs", "diamonds", "spades"]
        if len(deck) == 0:
            self.deck = []
            for s in suits:
                for n in numbers:
                    self.deck.append([s, n])
            shuffle(self.deck)
        else:
            self.deck = deck

        self.player_cards = p_cards
        self.dealer_cards = d_cards
        self.deal_first_two_cards()
    def deal_player(self):
        self.player_cards[self.curr_player].append(self.deck.pop())
        self.display()
    def deal_dealer(self):
        self.dealer_cards.append(self.deck.pop())
        self.display()
    def deal_first_two_cards(self):
        bc = False
        if len(self.dealer_cards) == 0:
            bc = True
            self.dealer_cards.append(["blank", "card"])
        while len(self.player_cards[self.curr_player]) < 2:
            self.deal_player()
        if bc == True:
            self.dealer_cards.pop()
            self.deal_dealer()
            self.deal_dealer()
        else:
            while len(self.dealer_cards) < 2:
                self.deal_dealer()

    def display(self, text="", pause=1):
        cv.destroyAllWindows()
        blank_card_img = cv.imread("PlayingCards/blank_card.png", cv.IMREAD_COLOR)
        text_box_img = cv.imread("PlayingCards/text_box.png", cv.IMREAD_COLOR)
        back_img = cv.imread("PlayingCards/back.png", cv.IMREAD_COLOR)
        print(self.player_cards)
        print(self.dealer_cards)
        max_length = max(len(self.player_cards[0]), len(self.player_cards[1]), len(self.dealer_cards))
        player_cards_img = card_to_image(self.player_cards[0][0])
        for i in range(1, max_length):
            if i < len(self.player_cards[0]):
                player_cards_img = np.concatenate((player_cards_img, card_to_image(self.player_cards[0][i])), axis=1)
            else:
                player_cards_img = np.concatenate((player_cards_img, blank_card_img), axis=1)

        if self.num_of_player == 2:
            second_player_cards_img = card_to_image(self.player_cards[1][0])
            for i in range(1, max_length):
                if i < len(self.player_cards[1]):
                    second_player_cards_img = np.concatenate((second_player_cards_img, card_to_image(self.player_cards[1][i])), axis=1)
                else:
                    second_player_cards_img = np.concatenate((second_player_cards_img, blank_card_img), axis=1)

            player_cards_img = np.concatenate((player_cards_img, second_player_cards_img), axis=0)

        dealer_cards_img = card_to_image(self.dealer_cards[0])
        for i in range(1, max_length):
            if i < len(self.dealer_cards):
                if self.dealer_card_show:
                    dealer_cards_img = np.concatenate((dealer_cards_img, card_to_image(self.dealer_cards[i])), axis=1)
                else:
                    dealer_cards_img = np.concatenate((dealer_cards_img, back_img), axis=1)
            else:
                dealer_cards_img = np.concatenate((dealer_cards_img, blank_card_img), axis=1)

        text_box_imgs = text_box_img
        for i in range(1, max_length):
            text_box_imgs = np.concatenate((text_box_imgs, text_box_img), axis=1)

        img = np.concatenate((player_cards_img, dealer_cards_img, text_box_imgs), axis=0)

        cv.putText(img, "Player" + str(self.curr_player + 1) + "'s Score: " + str(calculate_score(self.player_cards[self.curr_player])), (10, 360+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)

        #outline curr green
        if self.dealer_card_show:
            cv.rectangle(img, (0, 330 * 2), (img.shape[1], 330 + 330 * 2), (0, 255, 0), 2)
        else:
            cv.rectangle(img, (0, 330 * self.curr_player), (img.shape[1], 330 + 330 * self.curr_player), (0, 255, 0), 2)
        #outline cards red if the player lost or is losing
        if calculate_score(self.player_cards[0]) > 21 or (self.dealer_card_show and calculate_score(self.player_cards[0]) < calculate_score(self.dealer_cards)):
            cv.rectangle(img, (0, 0), (img.shape[1], 330), (0, 0, 255), 2)
        if self.num_of_player == 2:
            if calculate_score(self.player_cards[1]) > 21 or (self.dealer_card_show and calculate_score(self.player_cards[0]) < calculate_score(self.dealer_cards)):
                cv.rectangle(img, (0, 330), (img.shape[1], 660), (0, 0, 255), 2)

        if self.dealer_card_show:
            cv.putText(img, "Dealer's Score: " + str(calculate_score(self.dealer_cards)), (10, 380+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)
            cv.putText(img, "Dealer's Turn", (10, 400+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv.LINE_AA)
        else:
            cv.putText(img, "Dealer's Score: unknown", (10, 380+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)
            cv.putText(img, "Player" + str(self.curr_player + 1) + "'s Turn", (10, 400+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 0), 1, cv.LINE_AA)

        cv.putText(img, text, (10, 420+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)
        if self.num_of_player == 2:
            img = cv.resize(img, (0, 0), fx=0.8, fy=0.8)
        cv.imshow("BlackJack", img)
        cv.waitKey(1)
        time.sleep(pause)
        return
    def dealer_round(self):
        self.dealer_card_show = True
        self.display()
        while calculate_score(self.dealer_cards) < 16:
            self.dealer_cards.append(deck.pop())
            self.display()
        dealer_score = calculate_score(self.dealer_cards)
        if dealer_score > 21:
            self.display("Dealer Busted", 2)
            dealer_score = 0
        return dealer_score
    def player_round(self): #returns score and deck after.
        scores = []
        self.display("Player move: ", 0)
        player_move = get_player_input()
        self.display("Player move: " + player_move)
        time.sleep(1)
        while True:
            while player_move == "hit":
                self.deal_player()
                self.display()
                curr_score = calculate_score(self.player_cards[self.curr_player])
                if curr_score > 21:
                    self.display("Player Busted. You Loose", 2)
                    return [0], self.deck
                self.display("Player move: ", 0)
                player_move = get_player_input()
                self.display("Player move: " + player_move)
            if player_move == "stand":
                return [calculate_score(self.player_cards[self.curr_player])], self.deck
            elif player_move == "doubledown" and len(self.player_cards[self.curr_player]) == 2:
                self.display("Betsize is doubled. This is your last card. Good luck.")
                self.deal_player()
                self.display()
                curr_score = calculate_score(self.player_cards[self.curr_player])
                if curr_score > 21:
                    self.display("Player Busted. You Loose", 2)
                    return [0], self.deck
                else:
                    scores.append(calculate_score(self.player_cards[self.curr_player]))
                    return scores, self.deck
            elif player_move == "split" and self.num_of_player == 1 and len(self.player_cards[0]) == 2 and \
                    self.player_cards[0][0][1] == self.player_cards[0][1][1]:
                self.num_of_player = 2
                self.player_cards[1] = [self.player_cards[0][1]]
                self.player_cards[0] = [self.player_cards[0][0]]
                self.deal_first_two_cards()
                score1, self.deck = self.player_round()
                self.curr_player = 1
                self.deal_first_two_cards()

                score2, self.deck = self.player_round()
                scores = [score1[0], score2[0]]
                return scores, self.deck
            else:
                self.display("Illegal move. Please Choose another move.")
                self.display("Player move: ", 0)
                player_move = get_player_input()
                self.display("Player move: " + player_move)

#Gesture Sytem helper functions ------------------------------------------------------------------
def largest_contour(c_lst):
    # returns the contour with the largest area from a list of contours.
    l_area = 0
    l_cnt = None
    for c in c_lst:  # go through all contours in the list
        area = cv.contourArea(c)
        if area > l_area:  # if the area of the current contour is the largest encountered
            l_area = area  # set this area as the largest
            l_cnt = c  # set this contour as the largest contour
    return l_cnt  # return the largest contour

def find_hand_direction(center_x, center_y, handloc_hist, thresh_v, thresh_h):
    if handloc_hist[0][0] > center_x + thresh_h:
        direction_v = "left"
    elif handloc_hist[0][0] + thresh_h < center_x:
        direction_v = "right"
    else:
        direction_v = "none"

    if handloc_hist[0][1] > center_y + thresh_v:
        direction_h = "up"
    elif handloc_hist[0][1] + thresh_v < center_y:
        direction_h = "down"
    else:
        direction_h = "none"
    return (direction_v, direction_h)

def find_contour(frame):
    skin_lower = np.array([80, 135, 85], dtype="uint8")
    skin_upper = np.array([200, 200, 150], dtype="uint8")
    converted = cv.cvtColor(frame, cv.COLOR_BGR2YCR_CB)
    skinMask = cv.inRange(converted, skin_lower, skin_upper)
    img_contours, _ = cv.findContours(skinMask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    return largest_contour(img_contours)

def percentage(dir_lst, dir): #percentage of dir in dir_list
    if len(dir_lst) == 0:
        return 0
    count = 0
    for i in range(len(dir_lst)):
        if dir_lst[i] == dir:
            count += 1
    return count / len(dir_lst)

def percentage_e(dir_lst, dir, e): #percentage of dir in position e of dir_list
    if len(dir_lst) == 0:
        return 0
    count = 0
    for i in range(len(dir_lst)):
        if dir_lst[i][e] == dir:
            count += 1
    return count / len(dir_lst)

def find_closest_key_gesture(img_contour, key_gestures, key_gesture_threshold):
    min_diff = 1
    closest_match = -1  # index of the closest match.
    for i in range(len(key_gestures)):
        for example in key_gestures[i]:
            diff = cv.matchShapes(img_contour, example, cv.CONTOURS_MATCH_I1, 0) - key_gesture_threshold[i]
        if diff < min_diff:
            min_diff = diff
            closest_match = i
    return min_diff, closest_match

def initialize_key_gestures(key_gesture_name):
    key_gestures = [[],[]]
    cap = cv.VideoCapture(0)
    idx = 0
    skin_lower = np.array([80, 135, 85], dtype="uint8")
    skin_upper = np.array([200, 200, 150], dtype="uint8")
    picture_text = ["doubledown in low angle.", "doubledown in medium angle.", "doubledown in high angle.",
                    "split in low angle", "split in medium angle.", "split in high angle."]
    count = 0
    while True:
        _, frame = cap.read()
        converted = cv.cvtColor(frame, cv.COLOR_BGR2YCR_CB)
        skinMask = cv.inRange(converted, skin_lower, skin_upper)

        img_contours, _ = cv.findContours(skinMask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        # Find hand contour, and draw a rect.
        img_contour = largest_contour(img_contours)
        x, y, w, h = cv.boundingRect(img_contour)
        center_x, center_y = x + w // 2, y + h // 2
        cv.rectangle(skinMask, (x, y), (x + w, y + h), (255, 255, 255), 4)

        instruction_text = "Press t to take a picture of your " + picture_text[count] + " Gesture should directly face the camera."
        text_size, _ = cv.getTextSize(instruction_text, cv.FONT_HERSHEY_SIMPLEX, 0.7, 1)
        text_w, text_h = text_size
        cv.rectangle(skinMask, (5, 70), (15 + text_w, 95 + text_h), (255, 255, 255), -1)
        cv.putText(skinMask, instruction_text, (10, 90), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv.LINE_AA)
        cv.imshow("frame", skinMask)

        if cv.waitKey(1) == ord('t'):
            count += 1
            if count <= 3:
                key_gestures[0].append(img_contour)
            else:
                key_gestures[1].append(img_contour)
            if count >= 6:
                print("Moving On.")
                cap.release
                return key_gestures

def get_player_input():
    debug = False
    cap = cv.VideoCapture(0)
    handloc_memory = 5
    directions_memory = 20
    key_gesture_threshold = [0.12, 0.15]
    stay_still_threshold = 0.8
    handloc_hist = [(0, 0) for i in range(handloc_memory)]
    direction_hist = ["none" for i in range(directions_memory)]
    gesture_hist = ["none" for i in range(directions_memory)]
    no_movement_thresh = 10
    curr_key_gesture = "none"
    hit_stage = 0  # 0, 1, 2, 3, 4
    stand_stage = 0  # 0, 1, 2, 3, 4

    while True:
        _, frame = cap.read()
        img_contour = find_contour(frame)  # find hand contour
        # Draw a rect.
        x, y, w, h = cv.boundingRect(img_contour)
        center_x, center_y = x + w // 2, y + h // 2
        cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
        cv.circle(frame, (center_x, center_y), 2, (0, 0, 255), 2)

        # Find closest key gesture
        min_diff, closest_match = find_closest_key_gesture(img_contour, key_gestures, key_gesture_threshold)
        # Is the closest key gesture is close enough?
        if min_diff < 0:
            curr_key_gesture = key_gesture_name[closest_match]  # update curr gesture
            cv.putText(frame, curr_key_gesture + ": " + str(min_diff), (10, 110),
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1, cv.LINE_AA)
        else:
            curr_key_gesture = "none"
            cv.putText(frame, key_gesture_name[closest_match] + ": " + str(min_diff), (10, 110),
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1, cv.LINE_AA)
        # identify double down
        if curr_key_gesture == "doubledown":
            if percentage(gesture_hist, "doubledown") == 1 and percentage(direction_hist, ("none", "none")) > stay_still_threshold:
                cv.destroyAllWindows()
                return "doubledown"
        # identify split
        elif curr_key_gesture == "split":
            if percentage(gesture_hist, "split") == 1 and percentage(direction_hist, ("none", "none")) > stay_still_threshold:
                cv.destroyAllWindows()
                return "split"

        # identify hit
        hit_time_thresh = 3
        if percentage_e(direction_hist[-hit_time_thresh:], "up", 1) > 0.95 and percentage(direction_hist[-hit_time_thresh:], ("none", "up")) > 0.7:
            if hit_stage == 0 or hit_stage == 2:
                hit_stage += 1
        elif percentage_e(direction_hist[-hit_time_thresh:], "down", 1) > 0.95 and percentage(direction_hist[-hit_time_thresh:], ("none", "down")) > 0.7:
            if hit_stage == 1:
                hit_stage += 1
            elif hit_stage >= 3:
                cv.destroyAllWindows()
                return "hit"

        # identify stand
        stand_time_thresh = 4
        if percentage_e(direction_hist[-stand_time_thresh:], "left", 0) > 0.8:
            if stand_stage == 0 or stand_stage == 2:
                stand_stage += 1
        elif percentage_e(direction_hist[-stand_time_thresh:], "right", 0) > 0.8:
            if stand_stage == 1:
                stand_stage += 1
            elif stand_stage >= 3:
                cv.destroyAllWindows()
                return "stand"

        #reset stand and hit stage to 0 if there is no movement
        if percentage(direction_hist[-no_movement_thresh:], ("none", "none")) > 0.8:
            hit_stage = 0
            stand_stage = 0
        cv.putText(frame, "hitstage: " + str(hit_stage), (10, 330), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1, cv.LINE_AA)
        cv.putText(frame, "standstage: " + str(stand_stage), (10, 360), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1, cv.LINE_AA)

        # Find Hand direction
        hand_dir_v_thresh = 20
        hand_dir_h_thresh = 40
        direction = find_hand_direction(center_x, center_y, handloc_hist, hand_dir_v_thresh, hand_dir_h_thresh)

        # update history
        direction_hist.pop(0)
        direction_hist.append(direction)

        handloc_hist.pop(0)
        handloc_hist.append((center_x, center_y))

        gesture_hist.pop(0)
        gesture_hist.append(curr_key_gesture)
        #display camera if debugging
        if debug == True:
            cv.imshow("GestureRecognizer", frame)
            cv.resizeWindow("GestureRecognizer", 800, 700)
            cv.moveWindow("GestureRecognizer", 600, 0)

        if cv.waitKey(1) == ord('q'):
            # Turn off camera if key q is pressed
            cv.destroyAllWindows()
            cap.release
            return None

if __name__ == "__main__":
    # take picture of key gestures --------------------------------------------------------------------------------
    key_gesture_name = ["doubledown", "split"]
    key_gestures = initialize_key_gestures(key_gesture_name)

    # gameplay --------------------------------------------------------------------------------
    for i in range(15):
        ''' #activate for showing split
        numbers = ["ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king"]
        suits = ["hearts", "clubs", "diamonds", "spades"]
        deck = []
        for s in suits:
            for n in numbers:
                deck.append([s, n])
        deck.remove(["clubs", "10"])
        deck.remove(["hearts", "10"])
        shuffle(deck)
        thisgame = Game([[["clubs", "10"], ["hearts", "10"]],[]], [], deck)
        '''
        thisgame = Game([[],[]], [], [])
        #player's turn
        scores, deck = thisgame.player_round()
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