import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image,ImageOps
import os
import shutil
from math import floor,ceil,log

'''
pxtopt: determines font size based on height and a percentage
'''
def pxtopt(height,percent): # NOTE: 1px = .7pt
    if percent>1 or percent<=0:
        raise ValueError("percent not in range (0,1]")
    return int((percent*height)*.7)

'''
serialize: returns the corresponding image string of a card
'''
def serialize(card,path,living=True,armored=False):
    # make sure path has / at end
    path = path+"/" if path[-1]!="/" else path
    # check is the card is standard (not joker)
    if card.suit!=None:
        # get first character (first letter of suit)
        suit = card.suit[0]
        # get second character ([2,9]U[T,J,Q,K,A])
        val = "T" if card.value==10 else card.name[0] if card.value==1 or card.value>10 else str(card.value)
        # add extra characters if necessary ("X" if not living, "A" if armored)
        name = path+suit+val+str("" if card.value<=10 or living else "X")+str("A" if armored else "")+".png" 
        return name
    else:
        if "#1" in card.name: # colored joker
            return path+"JC.png"
        elif "#2" in card.name: # monotone (black & white) joker
            return path+"JM.png"
        else:
            raise ReferenceError("Card not recognized")    

# define constants (used in armor)
H = .15 # extra card size if E/W
V = .25 # extra card size if N/S
I = .23 # amount of pixels initial armor will take up (only used for vertical stacking (E/W))
S = .19 # size of cropped area (only used for vertical stacking (E/W))
T = .04 # % of pixels cropped from the top (only used for vertical stacking (E/W))

'''
armor: creates an underlayed armored royal image
c = cards [royal,armor,...]
p = path
l = living if true
o = orientation
b = border thickness
'''
def armor(cards,path,living,o,b):
    # check if this runs without any armor
    if len(cards)==1:
        raise ValueError("No armor supplied: "+cards)
    # create save name for royal
    name = serialize(cards[0],path,living,True)
    # get image of royal
    royal = Image.open(serialize(cards[0],path,living,False))
    # determine new size based on orientation
    w,h = royal.size
    if o=="N" or o=="S":
        h = h+ceil(V*h)+b
    elif o=="E" or o=="W":
        w = w+ceil(H*w)+b
    else:
        raise ValueError("orientation not recognized ("+o+")")
    # adjust cards to be an array of armor only
    cards = cards[1:] if len(cards)>1 else []
    # create the combined card (armored royal)
    armoredRoyal = Image.new("RGBA",(w,h))
    # loop through all aromor to be added
    for i in range(len(cards)):
        # get the image of the card
        armor = Image.open(serialize(cards[i],path))
        # get width and height of card
        wa,ha = armor.size
        if i==0: # first card
            # paste into final
            armoredRoyal.paste(armor,((floor(H*wa) if o=="E" else 0),(floor(V*ha) if o=="S" else 0)))
        else:
            # crop armor
            armor = armor.crop(((floor(wa-(H*wa)) if o=="S" else 0),\
                                (floor(ha-(T*ha)-(S*ha)) if o=="E" else floor(T*ha) if o=="W" else 0),\
                                (floor(H*wa) if o=="N" else wa),\
                                (floor(ha-(T*ha)) if o=="E" else floor((T*ha)+(S*ha)) if o=="W" else ha)))
            # add border
            armor = ImageOps.expand(armor,border=(b if o=="N" else 0,b if o=="W" else 0,b if o=="S" else 0,b if o=="E" else 0),fill="white")
            # paste into final
            '''
            x=0
            y=0
            if o=="N":
                x=floor(i*H*wa)
            elif o=="S":
                x=floor(w-((i+1)*H*wa))
                y=floor(V*ha)
            elif o=="E":
                x=floor(H*wa)
                y=floor(h-(i*S*ha)-(I*ha))
            elif o=="W":
                y=floor((I*ha)+(i*S*ha))
            else:
                raise ValueError("orientation not recognized ("+o+")")
            '''
            armoredRoyal.paste(armor,((floor(i*H*wa) if o=="N" else floor(w-((i+1)*H*wa)) if o=="S" else floor(H*wa) if o=="E" else 0),\
                                      (floor(h-(i*S*ha)-(I*ha)) if o=="E" else floor((I*ha)+((i-1)*S*ha)) if o=="W" else floor(V*ha) if o=="S" else 0)))
    # add border to royal
    royal = ImageOps.expand(royal,border=(b if o=="W" else 0,b if o=="N" else 0,b if o=="E" else 0,b if o=="S" else 0),fill="white")
    # paste into final
    armoredRoyal.paste(royal,((floor(H*wa) if o=="W" else 0),(floor(V*ha) if o=="N" else 0)))
    # save armored royal
    armoredRoyal.save(name)

'''
xify: overlays an X over a card
c = card image object
d = directory
n = name
'''
def xify(card,path,name):
    # make sure path has / at end
    path = path+"/" if path[-1]!="/" else path
    # check if a resized x already exists in fn dir
    if not os.path.isfile(path+"XR.png"):
        # open x as image
        x = Image.open("X.png")
        # resize x
        x.thumbnail(card.size)
        # save resized x
        x.save(path+"/XR.png")
    # set x to new x
    x = Image.open(path+"/XR.png")
    # get widths and heights of card and x
    w1,h1 = card.size
    w2,h2 = x.size
    # calculate coordinates for overlay
    x1 = int(.5*w1)-int(.5*w2)
    y1 = int(.5*h1)-int(.5*h2)
    x2 = int(.5*w1)+int(.5*w2)
    y2 = int(.5*h1)+int(.5*h2)
    if x2-x1<w2:
        x2+=(w2-x2+x1)
    if y2-y1<h2:
        y2+=(h2-y2+y1)
    # overlay X over card
    card.paste(x, (x1,y1,x2,y2), x)
    # save new card
    card.save(path+"/"+name+"X.png")

'''
resize: resizes deck of choice
- w = screen width
- h = screen height
- r = rows
- c = columns
- a = array of anomalies ordered by [[size,number of occurances,horizontal/vertical]]
- t = text [[size,# of lines]]
- x = overlay x (specifically for gridcannon) (T/F)
- rd = reference directory
- nd = new directory
'''
def resize(w,h,r,c,a,t,x,rd,nd):
    # remove existing dir if there is one
    if os.path.isdir(nd):
        shutil.rmtree(nd)
    # make sure anomalies does not exceed number of rows or columbs
    if sum([sn[0] for sn in a])>c or sum([sn[0] for sn in a])>r:
        raise ValueError("number of anomalies exceeds number of rows/columns")
    # sum all products of anomalies and all number of occurences along with products of text lines and sizes
    vp = sum([(sn[0]*sn[1]) for sn in a if sn[2].upper()=="V"])
    vo = sum([sn[1] for sn in a if sn[2].upper()=="V"])
    hp = sum([(sn[0]*sn[1]) for sn in a if sn[2].upper()=="H"])
    ho = sum([sn[1] for sn in a if sn[2].upper()=="H"])
    st = sum([(((6.26118*log(55.3806,.422873*sn[0]))-4.15094)*sn[0]*sn[1]) for sn in t])
    # determine maximum card dimensions
    # mw = w/(c-2+(2*a)) # NOTE: Constant method
    mw = floor(w/(c-ho+hp))
    mh = floor((h-st)/(r-vo+vp))
    d = min(mw,mh) 
    # NOTE: debugging
    # print("w: "+str(w)+"\nh: "+str(h)+"\nvp: "+str(vp)+"\nvo: "+str(vo)+"\nhp: "+str(hp)+"\nho: "+str(ho)+"\nst: "+str(st)+"\nmw: "+str(mw)+"\nmh: "+str(mh))
    # create a new dir to store the resized cards
    os.mkdir(nd)
    # loop through all cards in Standard, resize them, and put them in the new dir
    for img in os.listdir(rd):
        # open card as image
        card = Image.open(rd+"/"+str(img))
        # resize using thumbnail
        card.thumbnail((d,d))
        # save the card
        card.save(nd+"/"+str(img))
        # if royal, save version with x
        if x and (img[1]=="J" or img[1]=="Q" or img[1]=="K"):
            xify(card,nd,str(img)[:-4])