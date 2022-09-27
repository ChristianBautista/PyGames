from card import Card
import random

# constant vars
suits = ["Clubs", "Diamonds", "Hearts", "Spades"]

# TODO: Add functionality for different types of decks
class Deck:
    def __init__(self,jok,bj):
        self.deck = []
        self.disc = []
        for i in range(4):
            for j in range(13):
                v = j+1
                n = str(v)
                if v==1:
                    n = "Ace"
                elif v==11:
                    n = "Jack"
                elif v==12:
                    n = "Queen"
                elif v==13:
                    n = "King"
                if bj:
                    v = [1,11]
                self.deck.append(Card(v,suits[i],n,True))
        if jok:
            self.deck.append(Card(0,None,"Joker #1",False))
            self.deck.append(Card(0,None,"Joker #2",False))
    def empty(self):
        return False if self.deck else True
    def shuffle(self):
        random.shuffle(self.deck)
    def draw(self):
        c = self.deck[0]
        self.disc.append(c)
        self.deck.pop(0)
        return c
    def replace(self,cards,top):
        self.deck = cards+self.deck if top else self.deck+cards
        self.disc = [c for c in self.disc if not c in cards]
    def reset(self):
        self.deck.extend(self.disc)
    def set(self,order):
        for index,card in order.items():
            if card[0]==0 and (card[1]=="C" or card[1]=="Color"):
                card = self.deck.pop([i for i in range(len(self.deck)) if self.deck[i].name=="Joker #1"][0])
            elif card[0]==0 and (card[1]=="M" or card[1]=="Monotone"):
                card = self.deck.pop([i for i in range(len(self.deck)) if self.deck[i].name=="Joker #2"][0])
            else:
                card = self.deck.pop([i for i in range(len(self.deck)) if (self.deck[i].value==card[0] and (self.deck[i].suit==card[1] or self.deck[i].suit[0]==card[1].upper()))][0])
            self.deck.insert(index,card)
    def __str__(self):
        res = ""
        for c in self.deck:
            res+=str(c)+"\n"
        return res[:-1]

