import argparse
import random
import sys
import numpy as np
from os import path
import time


class colour:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    MAGENTA = '\u001b[35;1m'
    WARNING = '\033[93m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


ap = argparse.ArgumentParser()

help_string = "The direction you want to be tested on. Choose either:" \
              "-db: decimal=>binary" \
              "-bd: binary=>decimal" \
              "-rand: alternates between the two randomly"

ap.add_argument("direction", choices=['db', 'bd', 'rand'], help=help_string)

ap.add_argument("-u", "--user", required=False,
                help="(optional) your name or what you want your scores to be saved as")
ap.add_argument("-n", "--number", nargs="?", type=int, default=6) #? means 1 or 2 args
ap.add_argument("-b", "--base", nargs='?', default=2, type=int,
                help="(optional) what base: 2=10 or 3=_+")
#NB base 3 takes same direction choices but obviously bd means ternary => decimal
args = ap.parse_args()


direction = args.direction

spath = "scores" + str(args.base) + ".txt"
if args.user:
    spath = args.user + ".txt"

"""add = False
if len(sys.argv)  > 1:
    direction = sys.argv[1]
    if direction == 'add':
        spath = "add.txt"
        add = True
    if len(sys.argv) == 3:
        spath = sys.argv[2] + ".txt" """
#print(direction)

def tern(num):
    ts = np.base_repr(num, base=3)
    #ts = ts.replace("1", "|_").replace("2", "|¯")
    ts = ts.replace("0", "+").replace("1", "_").replace("2", "¯")
    return ts

def dec(num):
    #st = num.replace("|_", "1").replace("|¯", "2")
    st = num.replace("+", "0").replace("_", "1").replace("¯", "2")
    return int(st, 3)

def get_ans(x, seed=2):
    if direction == 'bd' or seed == 0:
        try:
            if args.base == 2:
                val = int( input('{0:b}'.format(x) + ' in decimal = ').replace(" ", "") )
            elif args.base == 3:
                val = int(input(tern(x) + ' in decimal = ').replace(" ", ""))
        except ValueError:
            print(colour.WARNING + "that's wrong and not even in the right way" + colour.END)
            print("Remember to enter -1 to end (or -2 to end with a description of your accuracy)")
            val = get_ans(x,seed=seed)
        return val
    elif direction == 'db' or seed == 1:
        try:
            if args.base == 2:
                val = int(input( '' +  str(x) + ' in binary = ').replace(" ", ""), 2)
            elif args.base == 3:
                val = dec(input(str(x) + ' in ternary = ').replace(" ",""))
        except ValueError:
            base = "binary"
            if args.base == 3: base = "ternary"
            print(colour.WARNING + "in", base, "you fool" + colour.END)
            val = get_ans(x, seed=seed)
        return val
    elif direction == 'rand':
        rand = random.randint(0,1)
        return get_ans(x, seed=rand)

def checkUp(score, total, mx, scores,last_c):
    if total - last_c < mx:
        return False
    if scores[-1][0] < 3:
        return False
    if mx < 16:
        return total % mx == 0
    if total % 25 != 0:
        return False
    if score / total < 0.9:
        return False
    return True
#print('add timing stuff?')
#f = open("vals.txt", "w+") #a+ for appending
#f = open("vals.txt", "r")
#maxx = int(f.read())
#f.close()
print(colour.BOLD + colour.UNDERLINE + colour.BLUE + colour.GREEN + "welcome to binaryte" + colour.END)

if args.base == 3:
    print("remember, 0 =", tern(0), ", 1 =", tern(1), ", 2 =", tern(2))

path_bool = path.exists(spath)
if not path_bool:
    print(colour.CYAN + "hi " + colour.PURPLE + (spath.split(".txt")[0]) + colour.CYAN + " you're new and there's no file to save your progress in" + colour.END)
    path_bool = input('please can I make one: y/n ') == "y"
    print("ok")
    if path_bool:
        l = ""
        for n in range(args.number):
            l += str(n) + " 0 1\n"
        l += "total " + str(n+1) + " " + str(n+1)
        text_file = open(spath, "w")
        text_file.write(l)
        text_file.close()

lines = None
if not path_bool:
    lines = []
    for n in range(args.number):
        lines.append(str(n) + " 0 1")
    lines.append("total " + str(n+1) + " " + str(n+1))
    """lines = ["0 0 1",
            "1 0 1",
            "2 0 1",
            "3 0 1",
            "4 0 1",
            "5 0 1",
             "total 6 6"]"""

if path_bool:
    g = open(spath, "r")
    lines = g.readlines()
    g.close()

maxx = int(lines[-1].split(' ')[-1])
print(colour.CYAN + "current highpoint = " + str(maxx-1) + colour.END )

scores = np.zeros(shape=(maxx, 3))
dist = np.zeros(maxx)
#total = 0
for i in lines:
    s = i.split(' ')
    if s[0] == 'total':
        total = int(s[1])
    else:
        scores[int(s[0])][0] = int(s[1])
        scores[int(s[0])][1] = int(s[2])
        scores[int(s[0])][2] = int(s[1])/int(s[2])
        dist[int(s[0])] = 1 - max(0.0,int(s[1]) - int(s[0])/2) /int(s[2]) #what was I doing here?
dist /= np.sum(dist)


#print(scores[:,2])

#print(dist)
#x = random.randint(min,maxx)


local_score = 0
local_total = 0
localmax = maxx

x = np.random.choice(np.arange(0,localmax), p=dist)
ans = get_ans(x)

last_changed = 0

while ans >= 0:
    if ans==x:
        local_score+=1
        local_total+=1
        scores[x][0] += 1
        scores[x][1] += 1
        dist[x] /= 2
        if scores[x][0] < 10:
            dist[x] = max(1/localmax, dist[x])
        print(colour.GREEN + colour.BOLD + str(local_score) + "/" + str(local_total) + colour.END)
    else:
        local_total += 1
        scores[x][1] += 1
        dist[x] *= 2
        if ans < localmax: dist[ans] *= 4/3
        if args.base == 2:
            print(colour.RED + str(local_score) + '/' + str(local_total) + colour.END + ' (' + '{0:b}'.format(x) + ' = '+ str(x) + ')')
        elif args.base == 3:
            print(colour.RED + str(local_score) + '/' + str(local_total) + colour.END + ' (' + tern(x) + ' = '+ str(x) + ')')
    if checkUp(local_score,local_total, localmax, scores, last_changed):
        last_changed = local_total
        localmax += 1
        new_scores = np.zeros(shape=(localmax,3))
        new_scores[:-1] = scores
        new_scores[-1] = [0, 1, 0.0]
        scores = new_scores

        new_dist = np.zeros(localmax)
        new_dist[:-1] = dist
        new_dist[-1] = 1
        dist = new_dist

        print(colour.PURPLE + "congrats, new highest number = " +  str(localmax-1) + colour.END)

    dist /= np.sum(dist) #tanh to be snazzy?
    """if local_total % 100 == 0:
        print(colour.MAGENTA + "quick break?" + colour.END )
        print("take ", local_total/100)
        for i in range(int(local_total / 100)**2 ):
            print(colour.BOLD + colour.BLUE +  str(i + 1) + colour.END)
            time.sleep(1)"""
    x = np.random.choice(np.arange(0, localmax), p=dist)
    ans = get_ans(x)

if ans == -2:
    print("")
    for j in np.argsort(dist): #not working!!
        print(j, ": ", str.format('{:3f}', dist[-j]*100) , "%")

if path_bool:
    k = open(spath, "w+")
    for i in range(localmax):
        k.write(str(i) + " " + str(int(scores[i,0])) + " " +  str(int(scores[i,1])) + "\n")

    sum = total+local_total
    k.write("total " + str(sum) + " " + str(localmax) + "\n")
    k.close()

print(colour.WARNING + "initial highpoint was " +  str(maxx-1))
print(colour.GREEN + "you ended at " +  str(localmax - 1) + colour.END)
print(colour.PURPLE + "goodbye" + colour.END)