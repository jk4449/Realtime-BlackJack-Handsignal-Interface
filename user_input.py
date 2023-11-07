import cv2 as cv
import utils
import numpy as np

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

class GRS:
    #Gesture Recognition System
    def __init__(self):
        self.key_gesture_name = []
        self.key_gestures = []
    def initialize_key_gestures(self, key_gesture_name):
        self.key_gesture_name = key_gesture_name
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
            img_contour = utils.largest_contour(img_contours)
            x, y, w, h = cv.boundingRect(img_contour)
            center_x, center_y = x + w // 2, y + h // 2
            debug_image = skinMask.copy()
            cv.rectangle(debug_image, (x, y), (x + w, y + h), (255, 255, 255), 4)

            instruction_text = "Press t to take a picture of your " + \
                               picture_text[count] + " Gesture should directly face the camera."
            text_size, _ = cv.getTextSize(instruction_text, cv.FONT_HERSHEY_SIMPLEX, 0.7, 1)
            text_w, text_h = text_size
            cv.rectangle(debug_image, (5, 70), (15 + text_w, 95 + text_h), (255, 255, 255), -1)
            cv.putText(debug_image, instruction_text, (10, 90), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv.LINE_AA)
            cv.imshow("frame", debug_image)

            if cv.waitKey(1) == ord('t'):
                cv.imwrite("Ref_Images/img_" + str(count) + ".jpg", skinMask)
                count += 1
                if count <= 3:
                    key_gestures[0].append(img_contour)
                else:
                    key_gestures[1].append(img_contour)
                if count >= 6:
                    print("Moving On.")
                    cap.release
                    self.key_gestures = key_gestures
                    return key_gestures

    def get_player_input(self):
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
            img_contour = utils.find_contour(frame)  # find hand contour
            # Draw a rect.
            x, y, w, h = cv.boundingRect(img_contour)
            center_x, center_y = x + w // 2, y + h // 2
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
            cv.circle(frame, (center_x, center_y), 2, (0, 0, 255), 2)

            # Find closest key gesture
            min_diff, closest_match = utils.find_closest_key_gesture(img_contour, self.key_gestures, key_gesture_threshold)
            # Is the closest key gesture is close enough?
            if min_diff < 0:
                curr_key_gesture = self.key_gesture_name[closest_match]  # update curr gesture
                cv.putText(frame, curr_key_gesture + ": " + str(min_diff), (10, 110),
                           cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1, cv.LINE_AA)
            else:
                curr_key_gesture = "none"
                cv.putText(frame, self.key_gesture_name[closest_match] + ": " + str(min_diff), (10, 110),
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
            direction = utils.find_hand_direction(center_x, center_y, handloc_hist, hand_dir_v_thresh, hand_dir_h_thresh)

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