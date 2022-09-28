class Card:
    def __init__(self,v,s,n,c):
        self.value = v
        self.suit = s
        self.name = n
        if c:
            self.color = "B" if (s=="Clubs" or s=="Spades") else "R"
    def __str__(self):
        if self.suit==None:
            return self.name
        return self.name+" of "+self.suit