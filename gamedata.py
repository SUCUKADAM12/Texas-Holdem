import random
from holdem_hand_evaluator import evaluate_hand as evlhand



"""
2,3,4,5,6,7,8,9,T,j,q,k,a
spades,hearts,diamonds,clubs
"""
# example (game hasnt started) : players = [[playertoken1], [playertoken2] ... ]
#         (game has started) : players = [[playertoken1, [card1, card2]], [playertoken2, [card1, card2]] ... ]
class Game:
    def __init__(self):
        nums = ["2","3","4","5","6","7","8","9","T","J","Q","K","A"]
        suites = ["s", "h", "d", "c"]
        self.deck = []
        for s in suites:
            for n in nums:
                self.deck.append(n+s)

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self, amount = 1):
        c = ""
        a = amount
        while a > 0:
            c += self.deck[0]
            self.deck.remove(self.deck[0])
            a -= 1
        return c

    
    """
        comcards = card1 + card2 + card3 + card4 + card5
        plcards = [[card1 + card2, username1], [card1 + card2, useername2], [card1 + card2, username3]
    """
    def evaluate(self, comcards, plcards):
        evaluated = []
        evldusr = {}
        for cards in plcards:
            evldusr[evlhand(cards[0] + comcards)] = cards[1]
            evaluated.append(evlhand(cards[0] + comcards))
        evaluated.sort()
        evaluated.reverse()
        return evldusr[evaluated[0]]
            

if __name__ == "__main__":
    pass