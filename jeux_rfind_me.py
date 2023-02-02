#!/usr/bin/python3
import time
import math
import scan
import tkinter as tk
from tkinter import messagebox
import random
#début du main
ans=''        
welcome_message ="""

    Welcome to RFIND ME
    our players of today:
    
"""
def capture():
    tag=''
    while (tag==''):
        tag=scan.show_first_read_tag() 
    return tag

def evaluate_distance(Pr,Pt,Gr,Gt,freq,eps_r=1,mu_r=1):
    lmbda=(3*10**8)/(freq*mu_r*eps_r)
    R = (lmbda/(4*math.pi)) * math.sqrt((Pt*Gt*Gr)/Pr) 
    return(R/(R+1))

def timer(n:int):
    for i in range(0,n):
        print(n-i)
        time.sleep(1)

def play_sound():
    #find help online for this one
    print("")

def load_players(players_textfile="players.txt"):
    try:
        with open(players_textfile, "r") as file:
            file_content = file.read()
            players_list = [item.strip() for item in file_content.split(",")]
    except FileNotFoundError:
        with open(players_textfile, 'w') as fp:
            players_list=[]
    return players_list
    
def calibrate(nbplayers:int):
    #add prints here for prompts
    players=[]
    print ("Calibration for " + str(nbplayers) + " players")
    for i in range(1,nbplayers+1):
        pname="player #"+str(i)
        print("player #"+str(i)+", please write your name")
        b = input("$>")
        if (len(b[0])>0):
            pname=b
        print( pname, " please pass your tag in front of the antenna shortly")
        tag = capture()
        players.append([pname,tag])
        with open('players.txt', 'w') as fp:
            for item in players:
            # write each item on a new line
                fp.write("%s\n" % item)          
    return players

def name_of(tag,players):
    nam=""
    for player in players:
        if tag in player:
            nam = player[0]
            break
    return nam

def get_BB_settings():
    Pt = 1.58
    Gr = 1.64
    Gt = 7.07
    freq = 866.5*10**6
    return Pt,Gr,Gt,freq

def hide_and_seek(players):
    #print("press a key when ready to start the timer")
    print("3 seconds to hide!")
   # b = input("$>")
    timer(3)
    start=time.time()
    last=start
    caught=[]
    while (len(caught)<(len(players))):
        tag=capture()
        Pr = generate_random_Pr()
        Pt = 1.58
        Gr = 1.64
        Gt = 7.07
        freq = 866.6*10**6
        if (evaluate_distance(Pr,Pt,Gr,Gt,freq)<1):   
            if(tag not in caught):
                caught.append(tag)
                print(name_of(tag,players)+  " I found you !!!")
            if ((time.time() - last) > 2):
                print(str(round(evaluate_distance(Pr,Pt,Gr,Gt,freq),2)) + " metres")
                last=time.time()
        if (time.time()-start)>60:
            break
    print("caught list:")
    for tag in caught:
        print(name_of(tag,players)+ " tag:" + tag)
    return(caught)
            
def one_two_three_sun(players):
    print("press a key when ready to start the timer")
    b = input("$>")
    caught=['','']
    while (len(caught)<len(players)):
        for i in range(1,3):
            print(i)
            timer(i)
            play_sound()
        tag=capture() #all captures get caught
        caught.append(tag)

def on_calibrate():
    nbplayers = int(players_entry.get())
    players = calibrate(nbplayers)
    messagebox.showinfo("Info", "Players have been calibrated.")
    return players

def generate_random_Pr():
    return random.uniform(8.91*10**-2, 8.91*10**-6)

def on_hide_and_seek():
    caught = hide_and_seek(players)
    messagebox.showinfo("Info", "The game of hide and seek has finished.")
    return caught

def on_one_two_three_sun():
    one_two_three_sun(players)
    messagebox.showinfo("Info", "The game of one, two, three sun has finished.")

##game launch
print(welcome_message)
players=load_players()
players = [x.split("'") for x in ''.join(players).split('\n')]
players = [[x[1], x[3]] for x in players]
#print(players)
for player in players:
   print(player[0] + " with tag: " + player[1])
root = tk.Tk()
root.title("RFID Game Console")

players_label = tk.Label(root, text="Number of players:")
players_label.grid(row=0, column=0, padx=10, pady=10)

players_entry = tk.Entry(root)
players_entry.grid(row=0, column=1, padx=10, pady=10)

calibrate_button = tk.Button(root, text="Calibrate", command=on_calibrate)
calibrate_button.grid(row=1, column=0, padx=10, pady=10)

hide_and_seek_button = tk.Button(root, text="Hide and Seek", command=on_hide_and_seek)
hide_and_seek_button.grid(row=1, column=1, padx=10, pady=10)

one_two_three_sun_button = tk.Button(root, text="One, Two, Three Sun", command=on_one_two_three_sun)
one_two_three_sun_button.grid(row=2, column=0, padx=10, pady=10, columnspan=2)

root.mainloop()

'''
#reactivate this code if we can't use windows
while ans != 'exit':
    a = input("$>")
    a = a.split(" ")
    ans=a[0]  
    if ans == 'calibrate':
        print("how many player tags ?")
        b = input("$>")
        b = b.split(" ")
        nbplayers=int(b[0])  
        players=calibrate(nbplayers)
            
    if ans == 'hide and seek':
        hide_and_seek(players)
    if ans == 'soleil':
        one_two_three_sun(players)
    print(welcome_message)
'''