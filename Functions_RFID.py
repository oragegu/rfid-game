#!/usr/bin/python3

import time
import math
import scan2 as scan
#début du main
ans=''        
welcome_message ="""
write either:
    'exit'
    'calibrate'
    'hide and seek'
    'soleil'
"""
def capture():
    tag=''
    while (tag==''):
        tag=scan.show_first_read_tag()
    return tag

def evaluate_distance(Pr,Pe,Gr,Ge,freq,eps_r=1,mu_r=1):
    lmbda=(3*10**8)/(freq*mu_r*eps_r)
    R = (lmbda/(4*math.pi)) * math.sqrt((Pe*Ge*Gr)/Pr) 
    return(R)

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

def hide_and_seek(players):
    print("press a key when ready to start the timer")
    b = input("$>")
    timer(3)
    caught=['','']
    while (len(caught)<len(players)):
        tag=capture() #must include a wait/while system
        if (evaluate_distance()<1): #complete here    
            caught.append(tag)
            #remove tag from sought after tags (players)

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

print(welcome_message)
players=load_players()
print(players)
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
