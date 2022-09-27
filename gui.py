# imports
import tkinter as tk
import tkinter.ttk as ttk
import math
from gridcannon import init as gc
# global vars
initial = True
games = {
    "Individual": [
        ["Gridcannon", gc, False],
        ["Solitaire", None, False]
    ],
    "Versus": [
        ["Cuttle", None, False],
        ["Crazy Eights", None, False],
        ["Exploding Kittens", None, False],
        ["Golf", None, False],
        ["GOPS", None, False]
    ],
    "Gambling": [
        ["Blackjack", None, False],
        ["Poker", None, False],
        ["Sabacc", None, False],
        ["Yarsaboker", None, False]
    ]
}

# colmax
def colmax():
    # get length of rows (number of games per cat)
    rowlens = games.values()
    rowlens = map(lambda x: len(x), rowlens)
    # return max length of rows
    return max(rowlens)

# coldet
def coldet(l):
    # get colmax
    m = colmax()
    # determine if l>m
    if l>m:
        raise RuntimeError("System unable to properly identify max column length")
    elif l>=math.ceil(m/2):
        return (m-l+1),1
    else:
        if (m/l)%1==0:
            return (m/l),(m/l)
        else:
            i = math.floor(m/l)
            s = i+(m-(l*i))
            return s,i
    
# hover
def hover(b):
    # underline button text and change color to blue
    b.configure(font=("Comic Sans MS", 15, "underline"), fg="blue")

# leave
def leave(b):
    # un-underline button text and change color back to green
    b.configure(font=("Comic Sans MS", 15), fg="green")

# recreate: to be deleted
def recreate(menu,frame,info):
    if not games[info[0]][info[1]][2]:
        games[info[0]][info[1]][1].config(command=lambda: onClick(menu,frame))
        games[info[0]][info[1]][2] = True
    frame.place_forget()
    menu.place(anchor="c", relx=.5, rely=.5)

# onClick
def onClick(menu,frame,root=None,func=None,info=None):
    # destroy menu
    menu.place_forget()
    if frame==None:
        # run function
        func(root,menu,recreate,info)
    else:
        frame.place(anchor="c",relx=.5,rely=.5)

# menu
def menu(root):
    # create menu frame
    menu = tk.Frame(root, bg='black')
    # create title label with Magneto font
    title = tk.Label(menu, text="Captain's PyGames", font=("Magneto", 50), bg='black', fg='green')
    # get colmax
    m = colmax()
    # add title label to grid
    title.grid(row=0, column=0, columnspan=m)
    # define row
    r = 1
    # display all games as buttons
    global games
    for cat in games.keys():
        # create label for cat
        label = tk.Label(menu, text=cat, font=("Copperplate Gothic Bold", 35), bg='black', fg='green')
        # add label to grid
        label.grid(row=r, column=0, columnspan=m)
        # increment row and reset col
        r+=1
        c=0
        # create a button for each game in cat
        for game in games[cat]:
            # obtain span and increment
            span,inc = coldet(len(games[cat]))
            # store function for game from game[1]
            func = game[1]
            # create button for game
            game[1] = tk.Button(menu, text=game[0], font=("Comic Sans MS", 15), bg='black', fg='blue')
            # determine if active
            if func==None:
                # disable button
                game[1].config(state="disabled")
            else:
                # add func to button command
                game[1].config(fg="green",command=lambda f=func,c=cat,g=[i for i in range(len(games[cat])) if games[cat][i][0]==game[0]][0]: onClick(menu,None,root,f,[c,g]))
                # bind hover function
                game[1].bind("<Enter>", lambda e, b=game[1]: hover(b))
                # bind leave function
                game[1].bind("<Leave>", lambda e, b=game[1]: leave(b))
            # add button to grid
            game[1].grid(row=r, column=c, columnspan=span)
            # update col
            c+=inc
        # next row
        r+=1
    # pack & place menu frame
    menu.place(anchor="c", relx=.5, rely=.5)

def main():
    # creating window
    root = tk.Tk()
    # full screen
    root.state("zoomed")
    # title
    root.title("Captain's PyGames")
    # background color
    root.configure(background='black')

    # create and pack parent frame
    parent = tk.Frame(root, bg="black")
    parent.pack(fill="both", expand=True)

    # create canvas
    canvas = tk.Canvas(parent, bg="black")

    # create scrollbars
    x_scrollbar = tk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
    y_scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)

    # create mainframe and window in canvas
    mainframe = tk.Frame(canvas, bg="black")
    canvas.create_window((0, 0), window=mainframe, anchor="nw")
    canvas.update_idletasks()

    # configure canvas
    canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
    # canvas.configure(yscrollcommand=y_scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # pack all
    y_scrollbar.pack(side="right", fill="y")
    canvas.pack(fill="both", expand=True)
    x_scrollbar.pack(side="bottom", fill="x")

    # menu if initial
    global initial
    if initial:
        menu(mainframe)
        initial = False

    # create a frame, add a label in it and place it in the mainframe
    # frame = tk.Frame(mainframe, bg="black")
    # label = tk.Label(frame, text="Captain's PyGames", font=("Comic Sans MS", 50), bg='black', fg='green')
    # label.pack()
    # frame.pack()

    # run mainloop
    root.mainloop()

def mainNoScroll():
    # creating window
    root = tk.Tk()
    # full screen
    root.state("zoomed")
    # title
    root.title("Captain's PyGames")
    # background color
    root.configure(background='black')

     # menu if initial
    global initial
    if initial:
        menu(root)
        initial = False

    # run mainloop
    root.mainloop()

mainNoScroll()