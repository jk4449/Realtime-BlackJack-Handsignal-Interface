import numpy as np
import cv2 as cv
from random import shuffle
import time

#Game helper functions ------------------------------------------------------------------
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

