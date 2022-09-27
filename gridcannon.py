import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image,ImageTk
from functools import reduce
from img_man import *
from deck import Deck

'''
TODO List:
1. Dynamic Popup Frame: Lucida Calligraphy
2. Restart Function
3. Back Function
4. Saved States
5. Dynamic Font
'''

# backend vars
grid = []
royals = []
ploys = [] # Jokers,Aces
adjMat = [] # royal spaces adjacent to grid spaces
canMat = {} # grid index: royal indices: [cards in path]
# frames
gc = None # main frame
pu = None # popup frame
# UI references
gridUI = []
royalsUI = []
bottomUI = []
topUI = []
popupUI = []
# img references
gridIMGS = []
royalsIMGS = []
bottomIMGS = []
# object holders
deck = None # deck object
current = None # current card
# flags
ace = False # flag for ace
jok = False # flag for joker
emp = False # flag for empty deck
cur = False # flag for no current
live = True # flag for if the game is live
# constants
PT = 0 # font size
TOP = -1 # reference index to top of piles
IDN = "Gridcannon" # Image Directory Name
D = "OLW.png" # default image

# backend functions

def setup():
    # reset lists
    global grid
    grid = [[],[],[],[],[],[],[],[],[]]
    global royals
    royals = [[[],True],[[],True],[[],True],[[],True],[[],True],[[],True],[[],True],[[],True],[[],True],[[],True],[[],True],[[],True]]
    global ploys
    ploys = [[],[]] # Jokers,Aces
    global adjMat
    adjMat = [[0,3],[1],[2,4],[5],[],[6],[7,9],[10],[8,11]]
    global canMat
    canMat = { # grid index: royal indices: [cards in path]
        0: {
            4: [1,2],
            9: [3,6]
        },
        1: {
            10: [4,7]
        },
        2: {
            3: [0,1],
            11: [5,8]
        },
        3: {
            6: [4,5]
        },
        5: {
            5: [3,4]
        },
        6: {
            0: [0,3],
            8: [7,8]
        },
        7: {
            1: [1,4]
        },
        8: {
            2: [2,5],
            7: [6,7]
        }
    }
    # reset current and flags
    global current
    current = None
    global ace
    ace = False
    global jok
    jok = False
    global emp
    emp = False
    global cur
    cur = False
    global live
    live = True
    # create and shuffle a new deck with jokers
    global deck
    if deck==None:
        deck = Deck(True,False)
    else:
        deck.reset()
    deck.shuffle()
    # NOTE: debugging
    ''' # winning setup
    deck.set({
        0: [6,"H"],
        1: [7,"H"],
        2: [5,"D"],
        3: [7,"C"],
        4: [9,"H"],
        5: [7,"D"],
        6: [5,"C"],
        7: [7,"S"],
        8: [5,"S"],
        9: [12,"H"],
        10: [12,"D"],
        11: [12,"S"],
        12: [12,"C"],
        13: [13,"H"],
        14: [13,"D"],
        15: [13,"S"],
        16: [13,"C"],
        17: [11,"H"],
        18: [11,"D"],
        19: [11,"S"],
        20: [11,"C"],
        21: [6,"D"],
        22: [6,"S"],
        23: [6,"C"],
        24: [8,"H"],
        25: [10,"S"],
        26: [9,"D"],
        27: [10,"C"],
        28: [9,"S"],
        29: [10,"H"],
        30: [9,"C"],
        31: [10,"D"],
    })
    '''
    # loop until backend grid is filled
    royalstoplace = []
    i = 0
    while len([pile for pile in grid if not pile])>0:
        card = deck.draw()
        if card.value<=1: # ploy
            ploys[card.value]+=[card]
        elif card.value>=11: # royal
            royalstoplace+=[card]
        else:
            grid[i] = [card]
            i+=1
    # reverse order
    royalstoplace.reverse()
    # place royals back on top of the deck
    deck.replace(royalstoplace,True)

def turn():
    # declare vars
    global deck
    global current
    global royals
    global ploys
    global cur
    global emp
    global jok
    updDict = {
        "DC": [],
        "GA": [],
        "RA": [],
        "PA": [],
    }  
    # check if all royals are dead, if so, end the game
    if not [royal for royal in royals if royal[1]]:
        end(1)
        return
    # check if any royals have too much armor
    royVals = [[royal[0][0].value, sum([card.value for card in royal[0]])] for royal in royals if royal[0] and royal[1]]
    if [royVal for royVal in royVals if royVal[1]>20 or (royVal[0]==13 and royVal[1]>19)]:
        end(0)
        return
    # if there is no current and no cards left in the deck and no ploys, end the game, otherwise, draw a card
    if not current and deck.empty() and not ploys[0] and not ploys[1]:
        end(0)
        return
    elif not current and not deck.empty(): # current card was played and there are still cards in the deck
        current = deck.draw()
        updDict["DC"] = [2]
        if cur:
            cur = False
    elif not current and not cur: 
        cur = True
        updDict["DC"] = [2]
    # determine card type (normal, royal, or ploy)
    if current.value>10: # royal
        # find appropriatie positions to place royal and update
        updDict["RA"] = mostSimilar(current)
    elif current.value<=1: # ploy
        # append to appropriate ploy pile
        ploys[current.value].append(current)
        # NOTE: UI update handled on subsequent call of turn
        # remove current and call turn again
        current = None
        turn()
        return
    else:
        # determine if the card is placeable
        # get all the values of all the top cards in each pile
        global grid
        topVals = [(pile[TOP].value if pile else 0) for pile in grid]
        # determine which piles current can be placed
        placeable = [i for i in range(len(topVals)) if current.value>=topVals[i]]
        # determine if there are any royals to place armor on
        liveRoyals = [royal for royal in royals if royal[0] and royal[1]]
        # if not placeable and no royals to place armor and no ploys, end the game
        if not placeable and not liveRoyals and not ploys[0] and not ploys[1]:
            end(0)
            return
        elif placeable: # if placeable, activate piles
            updDict["GA"] = placeable
        elif liveRoyals: # if not placeable but there are royals to place armor, determine most similar royal
            updDict["RA"] = mostSimilar(current)

    # activate any ploys if there are any
    if not jok:
        updDict["PA"] = [(i*3) for i in range(len(ploys)) if ploys[i]]
    else:    
        jok = False

    # update deck UI
    if deck.empty() and not emp:
        emp = True
        updDict["DC"]+=[1]
    elif not deck.empty() and emp:
        emp = False
        updDict["DC"]+=[1]

    # perform UI update
    update([],[],updDict["DC"])
    activate(updDict["GA"],updDict["RA"],updDict["PA"])

'''
mostSimilar: determine which card in g is most similar to c 
c = card to be placed
inds = indices that are most similar
tops = group of cards to be compared to c (determined based on c (c>10: royal))

Use Cases:
1. placing a royal (g is grid)
2. adding armor to a royal (g is live royals)
'''
# TODO: specifically for armor, potentially account for added armor on royal
def mostSimilar(card):
    # declare vars
    global grid
    global adjMat
    global royals
    global TOP
    inds = []
    tops = []
    # determine use case (placing royal or armor)
    if card.value>10: # placing royal
        inds = [i for i in range(len(grid)) if grid[i] and adjMat[i]]
        tops = [(pile[TOP] if pile else None) for pile in grid]
    else: # placing armor
        inds = [i for i in range(len(royals)) if royals[i][0] and royals[i][1]]
        tops = [(royal[0][0] if (royal[0] and royal[1]) else None) for royal in royals] # NOTE: Line to change if editing use case
    # check for special case where potentially empty grid spaces next to unoccupied royal spaces and no live royals to place armor
    if not inds:
        if card.value>10: # return all unoccupied royal positions
            return reduce(lambda x,y: x+y, [pos for pos in adjMat if pos])
        else: # raise error, should already be handled in turn()
            raise RuntimeError("mostSimilar ran for armor placement when no living royals")
    # check if any cards in inds (referencing tops) have the same suit as c
    sim = [i for i in inds if tops[i].suit==card.suit]
    # if not, check if any cards in inds (referencing tops) have the same color as c
    if not sim:
        sim = [i for i in inds if tops[i].color==card.color]
    # if not, just get all indices
    if not sim:
        sim = inds
    # get max or min based on card
    inds = []
    m = 0 if card.value>10 else 20
    for i in sim:
        if (card.value>10 and tops[i].value>m) or (card.value<=10 and tops[i].value<m): # NOTE: Line to change if editing use case
            m = tops[i].value
            inds = [i]
        elif tops[i].value==m:
            inds.append(i)
    # return royal indices
    return reduce(lambda x,y: x+y, [adjMat[i] for i in inds]) if card.value>10 else inds

# NOTE: Only used for royals
'''
orientation: returns cardinal direction of royal index
r = royal index
s = sticky
'''
def orientation(r,s=False):
    if r<=2:
        return "S" if s else "N"
    elif r>=9:
        return "N" if s else "S"
    elif r%2==0:
        return "W" if s else "E"
    elif r%2==1:
        return "E" if s else "W"
    else:
        raise IndexError(str(r)+" is not in [0,11]")

def restart():
    # setup
    setup()
    # update all
    update([i for i in range(9)],[i for i in range(12)],[i for i in range(4)])
    # reactivate top buttons
    global topUI
    for b in topUI:
        b.config(state="normal")
    # place_forget pu
    global pu
    pu.place_forget()
    # turn
    turn()
    

def back(callback,menu,info,gi,ri,bi):
    # get vars
    global gc
    global live
    ''' NOTE: potentially do not need save state
    # backend vars
    global grid
    global royals
    global ploys
    global adjMat
    global canMat
    # frames
    global gc
    global pu
    # UI references
    gridUI = []
    royalsUI = []
    bottomUI = []
    topUI = []
    popupUI = []
    # img references
    gridIMGS = []
    royalsIMGS = []
    bottomIMGS = []
    # object holders
    global deck
    global current
    # flags
    global ace
    global jok
    global emp
    global cur
    # create a save state if necessary
    '''
    # check if the game has ended
    if not live:
        restart()
    else:
        close_popup(gi,ri,bi)
    # callback function menu frame and gc frame
    callback(menu,gc,info)

def end(result):
    # get vals
    global deck
    global royals
    global current
    global live
    # disable all buttons
    activate([],[],[])
    # compute score: sumVal(deadRoyals)
    score = sum([royal[0][0].value for royal in royals if not royal[1]])
    # compute bonus: sumVal(deck)+(20*aces)+(10*jokers)
    bonus = sum([(20 if card.value==1 else 10 if card.value==0 else card.value if card.value<=10 else 0) for card in deck.deck])+\
            (0 if not current else 20 if current.value==1 else 10 if current.value==0 else current.value if current.value<=10 else 0)+\
            (10*len(ploys[0]))+(20*len(ploys[1]))
    # determine if bonus should be added
    score = score+bonus if result==1 else score
    # set live to false
    live = False
    # open popup
    open_popup("Victory" if result==1 else "Defeat",score)

# frontend functions
def initFrame(callback,menu,info):
    # get vars
    global gc
    global pu
    global topUI
    global popupUI
    global PT
    # determine font size
    PT = pxtopt(gc.winfo_screenheight(),.06)
    # create all top row items
    title = tk.Label(gc, text="Gridcannon", font=("Harrington", PT), bg='black', fg='green')
    topUI = [None,None,None]
    topUI[0] = tk.Button(gc, text="←", font=("Harrington", int(PT/2)), bg='black', fg='green', command=lambda args=[callback,menu,info]: open_popup("Go Back?",back,args))
    topUI[1] = tk.Button(gc, text="↻", font=("Harrington", int(PT/2)), bg='black', fg='green', command=lambda: open_popup("Restart?",restart))
    topUI[2] = tk.Button(gc, text="?", font=("Harrington", int(PT/2)), bg='black', fg='green') # TODO: add command
    # add all to grid
    topUI[0].grid(row=0, column=0)
    topUI[1].grid(row=0, column=1)
    title.grid(row=0, column=2, columnspan=3)
    topUI[2].grid(row=0, column=6)
    # create separators
    sepMenu = ttk.Separator(gc, orient='horizontal')
    sepMenu.grid(row=1, column=0, columnspan=7, sticky="ew")
    sepBot = ttk.Separator(gc, orient='horizontal')
    sepBot.grid(row=7, column=1, columnspan=5, sticky="ew")
    # create popup frame
    pu = tk.Frame(gc, bg="black", highlightbackground="white", highlightthickness=2, width=int(gc.winfo_screenwidth()/4), height=int(gc.winfo_screenheight()/4))
    # create elements inside
    popupUI = [None,None,None,None] # NOTE: [prompt,yes,no,score]
    popupUI[0] = tk.Label(pu, font=("Lucida Calligraphy", PT), bg="black", fg="green")
    popupUI[1] = tk.Button(pu, text="Yes", font=("Script MT Bold", int(.75*PT)), bg="black", fg="green")
    popupUI[2] = tk.Button(pu, text="No", font=("Script MT Bold", int(.75*PT)), bg="black", fg="green")
    popupUI[3] = tk.Label(pu, font=("Old English Text MT", int(PT/2)), bg="black", fg="green")

def initGrid(r,c):
    # get all UI variables
    global gridUI
    gridUI = [None,None,None,None,None,None,None,None,None]
    global royalsUI
    royalsUI = [None,None,None,None,None,None,None,None,None,None,None,None]
    global bottomUI
    bottomUI = [None,None,None,None]
    global gridIMGS
    gridIMGS = [None,None,None,None,None,None,None,None,None]
    global royalsIMGS
    royalsIMGS = [None,None,None,None,None,None,None,None,None,None,None,None]
    global bottomIMGS
    bottomIMGS = [None,None,None,None]
    global grid
    global royals
    global ploys
    global TOP
    global IDN
    global D
    # create and store buttons for the main grid
    index = 0
    for i in range(3):
        for j in range(3):
            # get corresponding image and convert to ImageTk
            img = Image.open(serialize(grid[index][TOP],IDN)) if grid[index] else Image.open(IDN+"/"+D)
            img = ImageTk.PhotoImage(img)
            # store reference to image
            gridIMGS[index] = img
            # create a button for the image and store
            gridUI[index] = tk.Button(gc, image=img, bg='black', state="disabled", command=lambda ind=index: gridOnClick(ind))
            # add button to grid
            gridUI[index].grid(row=r+i+1, column=c+j+1)
            index+=1
    # create and store buttons for royals
    index = 0
    for i in range(5):
        for j in range(3 if i==0 or i==4 else 2):
            # get corresponding image and convert to ImageTk
            img = Image.open(serialize(royals[index][0][TOP],IDN)) if royals[index][0] else Image.open(IDN+"/"+D)
            img = ImageTk.PhotoImage(img)
            # store reference to image
            royalsIMGS[index] = img
            # create a button for the image and store
            royalsUI[index] = tk.Button(gc, image=img, bg='black', state="disabled", command=lambda ind=index: royalOnClick(ind))
            # add button to grid
            royalsUI[index].grid(row=(r+i), column=(c+j+1 if i==0 or i==4 else c+(4*j)), sticky=orientation(index,True))
            index+=1
    # create and store buttons for ploys
    for i in range(2):
        # get corresponding image and convert to ImageTk
        img = Image.open(serialize(ploys[i][TOP],IDN)) if ploys[i] else Image.open(IDN+"/"+D)
        img = ImageTk.PhotoImage(img)
        # store reference to image
        bottomIMGS[i*3] = img
        # create a button for the image and store
        bottomUI[i*3] = tk.Button(gc, image=img, bg='black', state="disabled", command=lambda ind=i: usePloy(ind))
        # add button to grid
        bottomUI[i*3].grid(row=(r+6), column=(c+(4*i)))
    # create and store image labels for deck and current
    img = Image.open(IDN+"/BG.png") # NOTE: card back image set here
    img = ImageTk.PhotoImage(img)
    bottomIMGS[1] = img
    bottomUI[1] = tk.Label(gc, image=img, bg='black')
    bottomUI[1].grid(row=(r+6), column=(c+1), columnspan=2)
    img = Image.open(IDN+"/"+D) 
    img = ImageTk.PhotoImage(img)
    bottomIMGS[2] = img
    bottomUI[2] = tk.Label(gc, image=img, bg='black')
    bottomUI[2].grid(row=(r+6), column=(c+2), columnspan=2)

'''
update: updates the images on buttons/labels
gi = list of grid indices to be updated
ri = list of royal indices to be updated
bi = list of bottomUI indicies to be updated
'''
def update(gi,ri,bi):
    # declare vars
    global grid
    global royals
    global ploys
    global deck
    global current
    global gridUI
    global royalsUI
    global bottomUI
    global gridIMGS
    global royalsIMGS
    global bottomIMGS
    global TOP
    global IDN
    global D
    # loop through all indicies in gif and update them on the grid
    for i in gi:
        # get corresponding image and convert to ImageTk
        img = Image.open(serialize(grid[i][TOP],IDN) if grid[i] else IDN+"/"+D)
        img = ImageTk.PhotoImage(img)
        # store reference to image
        gridIMGS[i] = img
        # configure button to new image
        gridUI[i].config(image=img)
    # loop through all indicies in rif and update them in royals
    for i in ri:
        # get corresponding image and convert to ImageTk
        img = Image.open(serialize(royals[i][0][0],IDN,royals[i][1],True if len(royals[i][0])>1 else False) if royals[i][0] else IDN+"/"+D)
        img = ImageTk.PhotoImage(img)
        # store reference to image
        royalsIMGS[i] = img
        # configure button to new image
        royalsUI[i].config(image=img)
    # loop through all indicies in biu and update them in bottomUI
    for i in bi:
        img = None
        # get corresponding image
        if i==1:
            img = Image.open(IDN+"/"+D if deck.empty() else IDN+"/BG.png") # NOTE: card back image set here
        elif i==2:
            img = Image.open(serialize(current,IDN) if current else IDN+"/"+D)
        else:
            img = Image.open(serialize(ploys[int(i/3)][TOP],IDN) if ploys[int(i/3)] else IDN+"/"+D)
        # convert image to ImageTk
        img = ImageTk.PhotoImage(img)
        # store reference to iage
        bottomIMGS[i] = img
        # configure button to new image
        bottomUI[i].config(image=img)

'''
activate: activates buttons based on indices given
gi = list of grid indices to be activated
ri = list of royal indices to be activated
bi = list of bottomUI indicies to be activated
'''
def activate(gi,ri,bi):
    # declare vars
    global gridUI
    global royalsUI
    global bottomUI
    # loop through grid and activate indices in gi, disabling all other indices
    for i in range(len(gridUI)):
        if i in gi and gridUI[i]['state']!="normal":
            gridUI[i].config(bg="yellow",state="normal")
        elif i not in gi and gridUI[i]['state']!="disabled":
            gridUI[i].config(bg="black",state="disabled")
    # loop through royals and activate indices in ri, disabling all other indices
    for i in range(len(royalsUI)):
        if i in ri and royalsUI[i]['state']!="normal":
            royalsUI[i].config(bg="yellow",state="normal")
        elif i not in ri and royalsUI[i]['state']!="disabled":
            royalsUI[i].config(bg="black",state="disabled")
    # loop through ploys and activate indices in bi, disabling all other indices
    for i in range(2):
        if (i*3) in bi and bottomUI[i*3]['state']!="normal":
            bottomUI[i*3].config(bg="yellow",state="normal")
        elif (i*3) not in bi and bottomUI[i*3]['state']!="disabled":
            bottomUI[i*3].config(bg="black",state="disabled")

'''
popup: opens and configures the popup window
prompt = text to display
func = function to run if user selects "Yes", or score if end state
args = [callback,menu,info] (only used for back)
'''
def open_popup(prompt,func,args=None):
    # get vars
    global pu
    global gridUI
    global royalsUI
    global bottomUI
    global topUI
    global live
    global PT
    # if game over, perform func automatically
    if not live and not isinstance(func,int):
        if args:
            func(args[0],args[1],args[2],[],[],[])
        else:
            func()
        return
    else:
        # configure prompt
        popupUI[0].config(text=prompt)
        # get all active buttons
        gi = [i for i in range(len(gridUI)) if gridUI[i]["state"]=="normal"]
        ri = [i for i in range(len(royalsUI)) if royalsUI[i]["state"]=="normal"]
        bi = [i for i in range(2) if bottomUI[i*3]["state"]=="normal"]
        # disable all buttons
        activate([],[],[])
        # check if there is a function or not
        if isinstance(func,int): # end state
            # hide 1 and 2
            # for i in range(2):
            #     if popupUI[i+1].winfo_ismapped():
            #         popupUI[i+1].place_forget()
            popupUI[1].place_forget()
            popupUI[2].place_forget()
            # config 0 (font) and 3 (text)
            popupUI[0].config(font=("Old English Text MT", PT))
            popupUI[3].config(text=str(func))
            # place labels
            popupUI[0].place(anchor="c", relx=.5, rely=.4)
            popupUI[3].place(anchor="c", relx=.5, rely=.6)
        else: # restart or go back
            # disable top buttons
            for b in topUI:
                b.config(state="disabled")
            # hide 3
            # if popupUI[3].winfo_ismapped():
            #     popupUI[3].place_forget()
            popupUI[3].place_forget()
            # config 0 font
            popupUI[0].config(font=("Lucida Calligraphy", PT))
            # config function to 1 and close_popup to 2
            if args:
                popupUI[1].config(command=lambda f=func,cb=args[0],m=args[1],i=args[2]: f(cb,m,i,gi,ri,bi))
            else:
                popupUI[1].config(command=lambda f=func: f())
            popupUI[2].config(command=lambda: close_popup(gi,ri,bi))
            # place buttons
            popupUI[0].place(anchor="c", relx=.5, rely=.35)
            popupUI[1].place(anchor="c", relx=.3, rely=.65)
            popupUI[2].place(anchor="c", relx=.7, rely=.65)
        # place popup frame
        pu.place(anchor="c", relx=.5, rely=.5)
        # raise frame
        pu.tkraise()

def close_popup(gi,ri,bi):
    # get vars
    global pu
    # place_forget popup
    pu.place_forget()
    # activate all buttons
    activate(gi,ri,bi)
    for b in topUI:
        b.config(state="normal")

# onClick functions
'''
Use Cases:
1. G - placing a card on a pile
    a. (backend) add card to pile in grid 
    b. (backend) check if any royal dies using canMat
    c. (frontend) update pile face in gridUI and if royal face in royalUI if royal dies
    d. (backend) set current to None and call turn
2. R - placing a royal 
    a. (backend) add card to appropriate index in royals
    b. (frontend) update royal face in royalsUI
    c. (backend) set current to None and call turn
3. R - placing armor on a royal
    a. (backend) add card to approriate index in royals
    b. (frontend) update royal button to have armor behind royal
    c. (backend) set current to None and call turn
4. P->G - using an ace to select a pile to pick up 
    1.a. (backend) determine which piles actually have cards
    1.b. (frontend) activate all piles that have cards to pick up and deactivate all royalsUI and bottomUI
    2.a. (backend) combine selected pile with deck and remove 1 ace from ploys
    2.b. (frontend) update selected pile face in gridUI as well as bottomUI
    2.c. (backend) DO NOT set current to None and call turn
5. P->G - using a joker to reassign a card from one pile to another 
    1.a. (backend) determine all viable cards to select (all cards that are greater than at least 1 card)
    1.b. (frontend) activate all piles that have cards to select and deactivate all royalsUI and bottomUI
    2.a. (backend) add current to the top of the deck and set selection as current
    2.b. (frontend) update pile with top card in gridUI and selected card in bottomUI
    2.c. (backend) call turn but DO NOT ALLOW PLOYS
'''

def gridOnClick(i):
    # get vars
    global grid
    global deck
    global current
    global ace
    global jok
    global TOP
    dri = [] # dead royal indices
    bitu = [] # bottom indices to update
    # determine use case
    if ace: # ace ploy selection
        # add pile (grid[i]) to the bottom of the deck
        deck.replace(grid[i],False)
        # clear grid[i]
        grid[i] = []
        # remove 1 ace from ploys
        ploys[1].pop(-1)
        # turn off ace flag
        ace = False
        # add indices to update to bitu
        bitu = [1,3]
    elif jok: # joker ploy selection
        # add current to the top of the deck
        deck.replace([current],True)
        # set current to grid[i][TOP]
        current = grid[i][TOP]
        # remove top card from grid[i]
        grid[i].pop(TOP)
        # remove 1 joker from ploys
        ploys[0].pop(-1)
        # add indices to update to bitu
        bitu = [0,2]
    else:
        # add current to grid[i]
        grid[i]+=[current]
        # check for potentially dead royals using canMat
        global canMat
        global royals
        if i in canMat.keys():
            for r,g in canMat[i].items(): # r = royal index, g = grid indices
                # only run if there is a royal
                if royals[r][0]:
                    # get the royal
                    royal = royals[r][0][0]
                    # determine which cards can be used to attack the royal
                    vals = []
                    if royal.value==13: # king
                        vals = [(grid[gi][TOP].value if grid[gi] and grid[gi][TOP].suit==royal.suit else 0) for gi in g]
                    elif royal.value==12: # queen
                        vals = [(grid[gi][TOP].value if grid[gi] and grid[gi][TOP].color==royal.color else 0) for gi in g]
                    elif royal.value==11: # jack
                        vals = [(grid[gi][TOP].value if grid[gi] else 0) for gi in g]
                    else: # not a royal
                        raise ValueError(str(royal)+" is not a royal")
                    # check if royal dies
                    if sum(vals)>=sum([card.value for card in royals[r][0]]):
                        # set royal to false
                        royals[r][1] = False
                        # add r to dri
                        dri+=[r]
                        # if armor, create new image # NOTE: Subject to change (show armor on dead royal or not)
                        if len(royals[r][0])>1:
                            global IDN
                            armor(royals[r][0],IDN,royals[r][1],orientation(r),1) # NOTE: border width set here to 1
            # remove dead royal indices from 
            [canMat[i].pop(r) for r in dri]
            # check to see if no more live royals attacked
            if not canMat[i]:
                canMat.pop(i) 
        # set current to None
        current = None
    # update selected pile's face
    update([i],dri,bitu)
    # call turn
    turn()

def royalOnClick(i):
    # get vars
    global royals
    global current
    # add card to appropriate royal index
    royals[i][0]+=[current]
    # check current to determine if armor or royal placement
    if current.value>10: # if royal, remove from adjMat
        global adjMat
        index = [x for x in range(len(adjMat)) if i in adjMat[x]] # should only be length 1
        if len(index)!=1:
            raise ValueError("more than one or no occurence of "+str(i)+" in adjMat")
        adjMat[index[0]].remove(i)
    else:
        # create image
        global IDN
        armor(royals[i][0],IDN,royals[i][1],orientation(i),1) # NOTE: border width set here to 1
    # update face
    update([],[i],[])
    # set current to None
    current = None
    # call turn
    turn()

def usePloy(t):
    # get vars
    global grid
    indices = []
    # determine type of ploy used
    if t==1:
        # set ace flag to true
        global ace
        ace = True
        # get all grid indices of piles with cards
        indices = [i for i in range(len(grid)) if grid[i]]
    elif t==0:
        # set joker flag to true
        global jok
        jok = True
        # get all topVals
        topVals = [(pile[TOP].value if pile else 0) for pile in grid]
        # only get indices of cards that are greater than at least 1 or more cards
        for i in range(len(topVals)):
            if topVals[i]!=0:
                for j in range(len(topVals)):
                    if i==j or topVals[i]<topVals[j]:
                        continue
                    else:
                        indices+=[i]
                        break
    else:
        raise ValueError("Ploy Type ("+t+") not recognized")
    # update gridUI
    activate(indices,[],[])

# init
def init(root,menu,callback,info):
    # create frame
    global gc
    gc = tk.Frame(root,bg="black")
    # setup grid in backend
    setup()
    # initialize gui elements in frame
    initFrame(callback,menu,info)
    # resize the entire deck and store in a dir called Gridcannon
    global PT
    global IDN
    resize(gc.winfo_screenwidth(), gc.winfo_screenheight(), 6, 5, [[1.15,2,"H"],[1.25,2,"V"]], [[PT,1]], True, "Standard", IDN)
    # initialize grid gui
    initGrid(2,1)
    # place gc frame
    gc.place(anchor="c", relx=.5, rely=.5)
    # play the first turn
    turn()
    '''
    global gc
    # check for saved state
    if ss: # TODO:
        pass
    else:
        # create frame
        gc = tk.Frame(r,bg="black")
        # setup grid in backend
        setup()
        # initialize gui elements in frame
        initFrame(cb,m)
    # NOTE: On restarts/saved states, reconfigure font
    # resize the entire deck and store in a dir called Gridcannon
    global PT
    global IDN
    resize(gc.winfo_screenwidth(), gc.winfo_screenheight(), 6, 5, [[1.15,2,"H"],[1.25,2,"V"]], [[PT,1]], True, "Standard", IDN)
    # initialize grid gui
    initGrid(2,1)
    # place gc frame
    gc.place(anchor="c", relx=.5, rely=.5)
    # play the first turn
    turn()
    '''