import numpy as np
import cv2 as cv
from random import shuffle
import time
import utils
import user_input

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
        max_length = max(len(self.player_cards[0]), len(self.player_cards[1]), len(self.dealer_cards))
        player_cards_img = utils.card_to_image(self.player_cards[0][0])
        for i in range(1, max_length):
            if i < len(self.player_cards[0]):
                player_cards_img = np.concatenate((player_cards_img, utils.card_to_image(self.player_cards[0][i])), axis=1)
            else:
                player_cards_img = np.concatenate((player_cards_img, blank_card_img), axis=1)

        if self.num_of_player == 2:
            second_player_cards_img = utils.card_to_image(self.player_cards[1][0])
            for i in range(1, max_length):
                if i < len(self.player_cards[1]):
                    second_player_cards_img = np.concatenate((second_player_cards_img, utils.card_to_image(self.player_cards[1][i])), axis=1)
                else:
                    second_player_cards_img = np.concatenate((second_player_cards_img, blank_card_img), axis=1)

            player_cards_img = np.concatenate((player_cards_img, second_player_cards_img), axis=0)

        dealer_cards_img = utils.card_to_image(self.dealer_cards[0])
        for i in range(1, max_length):
            if i < len(self.dealer_cards):
                if self.dealer_card_show:
                    dealer_cards_img = np.concatenate((dealer_cards_img, utils.card_to_image(self.dealer_cards[i])), axis=1)
                else:
                    dealer_cards_img = np.concatenate((dealer_cards_img, back_img), axis=1)
            else:
                dealer_cards_img = np.concatenate((dealer_cards_img, blank_card_img), axis=1)

        text_box_imgs = text_box_img
        for i in range(1, max_length):
            text_box_imgs = np.concatenate((text_box_imgs, text_box_img), axis=1)

        img = np.concatenate((player_cards_img, dealer_cards_img, text_box_imgs), axis=0)

        cv.putText(img, "Player" + str(self.curr_player + 1) + "'s Score: " + str(utils.calculate_score(self.player_cards[self.curr_player])), (10, 360+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)

        #outline curr green
        if self.dealer_card_show:
            cv.rectangle(img, (0, 330 * 2), (img.shape[1], 330 + 330 * 2), (0, 255, 0), 2)
        else:
            cv.rectangle(img, (0, 330 * self.curr_player), (img.shape[1], 330 + 330 * self.curr_player), (0, 255, 0), 2)
        #outline cards red if the player lost or is losing
        if utils.calculate_score(self.player_cards[0]) > 21 or \
                (self.dealer_card_show and utils.calculate_score(self.player_cards[0]) < utils.calculate_score(self.dealer_cards)):
            cv.rectangle(img, (0, 0), (img.shape[1], 330), (0, 0, 255), 2)
        if self.num_of_player == 2:
            if utils.calculate_score(self.player_cards[1]) > 21 or \
                    (self.dealer_card_show and utils.calculate_score(self.player_cards[0]) < utils.calculate_score(self.dealer_cards)):
                cv.rectangle(img, (0, 330), (img.shape[1], 660), (0, 0, 255), 2)

        if self.dealer_card_show:
            cv.putText(img, "Dealer's Score: " + str(utils.calculate_score(self.dealer_cards)),
                       (10, 380+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)
            cv.putText(img, "Dealer's Turn",
                       (10, 400+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv.LINE_AA)
        else:
            cv.putText(img, "Dealer's Score: unknown",
                       (10, 380+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)
            cv.putText(img, "Player" + str(self.curr_player + 1) + "'s Turn",
                       (10, 400+330*(self.num_of_player)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 0), 1, cv.LINE_AA)

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
        while utils.calculate_score(self.dealer_cards) < 16:
            self.dealer_cards.append(self.deck.pop())
            self.display()
        dealer_score = utils.calculate_score(self.dealer_cards)
        if dealer_score > 21:
            self.display("Dealer Busted", 2)
            dealer_score = 0
        return dealer_score
    def player_round(self, grs): #returns score and deck after.
        scores = []
        self.display("Player move: ", 0)
        player_move = grs.get_player_input()
        self.display("Player move: " + player_move)
        time.sleep(1)
        while True:
            while player_move == "hit":
                self.deal_player()
                self.display()
                curr_score = utils.calculate_score(self.player_cards[self.curr_player])
                if curr_score > 21:
                    self.display("Player Busted. You Loose", 2)
                    return [0], self.deck
                self.display("Player move: ", 0)
                player_move = grs.get_player_input()
                self.display("Player move: " + player_move)
            if player_move == "stand":
                return [utils.calculate_score(self.player_cards[self.curr_player])], self.deck
            elif player_move == "doubledown" and len(self.player_cards[self.curr_player]) == 2:
                self.display("Betsize is doubled. This is your last card. Good luck.")
                self.deal_player()
                self.display()
                curr_score = utils.calculate_score(self.player_cards[self.curr_player])
                if curr_score > 21:
                    self.display("Player Busted. You Loose", 2)
                    return [0], self.deck
                else:
                    scores.append(utils.calculate_score(self.player_cards[self.curr_player]))
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
                player_move = grs.get_player_input()
                self.display("Player move: " + player_move)