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

ap.add_argument("-u", "--user", required=False,
                help="(optional) your name or what you want your scores to be saved as")

args = ap.parse_args()

print(colour.BOLD + colour.UNDERLINE + colour.BLUE + colour.GREEN + "welcome to binaradd?" + colour.END)

spath = "add_scores.txt"
if args.user:
    spath = args.user + ".txt"


path_bool = path.exists(spath)
if not path_bool:
    print(colour.CYAN + "hi " + colour.PURPLE + (spath.split(".txt")[0]) + colour.CYAN + " you're new and there's no file to save your progress in" + colour.END)
    path_bool = input('please can I make one: y/n ') == "y"
    print("ok")
    if path_bool:
        text_file = open(spath, "w")
        text_file.write(
"""0 0_1 0_1 0_1 0_1
1 0_1 0_1 0_1 0_1
2 0_1 0_1 0_1 0_1
3 0_1 0_1 0_1 0_1
total 16 4
""")
        text_file.close()

lines = None
if not path_bool:
    lines = ["0 0_1 0_1 0_1 0_1",
            "1 0_1 0_1 0_1 0_1",
            "2 0_1 0_1 0_1 0_1",
            "3 0_1 0_1 0_1 0_1",
             "total 16 4"]

if path_bool:
    g = open(spath, "r")
    lines = g.readlines()
    g.close()

maxx = int(lines[-1].split(' ')[-1])
print(colour.CYAN + "current highpoint = " + str(maxx-1) + colour.END )


scores = np.zeros(shape=(maxx, maxx, 3)) #scores[x][y] is a vector of the correct and total number of times x + y has been asked
dist = np.zeros(shape=(maxx,maxx))
total = lines[-1].split(' ')[-2]
for line in lines[:-1]:
    row = line.split(' ')
    x = int(row[0])
    for y in range(len(row[1:])):
        both = row[1+y].split('_')
        scores[x][y][0] = int(both[0])
        scores[x][y][1] = int(both[1])
        scores[x][y][2] = int(both[0])/int(both[1])
    dist[x] = 1 - scores[x][:,2]


def get_sum(x,y):
    return int(input('{0:b}'.format(x) + " + " + '{0:b}'.format(y) + " = "), 2)

local_score = 0
local_total = 0
last_changed = 0
localmax = maxx

x_dist = np.sum(dist,axis=0) # x's distribution should be in general bad a number is
x = np.random.choice(np.arange(0,localmax), p=x_dist/np.sum(x_dist))

y_dist = dist[x]/np.sum(dist[x]) #y's distribution should be how correct the sums tend to be given x
y = np.random.choice(np.arange(0,localmax), p=y_dist)

ans = get_sum(x,y)

while ans >= 0:
    if ans == x + y:
        scores[x][y][0] += 1
        scores[x][y][1] += 1
        #make symmetric?  ie also do scores[y][x][0] +=1 etc
        local_score += 1
        local_total += 1
        dist[x][y] /= 2
        #if scores[x][y][0] < 10:
        #    dist[x] = max(1/localmax, dist[x]) this would be nice but what is max between two arrays?
        print(colour.GREEN + colour.BOLD + str(local_score) + "/" + str(local_total) + colour.END)
    else:
        scores[x][y][1] += 1
        local_total += 1
        dist[x][y] *= 2
        print(colour.RED + str(local_score) + '/' + str(local_total) + colour.END + ' (' + '{0:b}'.format(x) + " + " + '{0:b}'.format(y) +  ' = ' + '{0:b}'.format(x+y) + ')')


    if local_total % min((last_changed-localmax) * 2, 25) == 0 and local_score/local_total > 0.9: # and scores[-1][0] > 3:
        last_changed = local_total #not working quite
        localmax +=1
        new_scores = np.zeros(shape=(localmax,localmax,3))
        new_scores[:-1,:-1] = scores
        new_scores[:,-1] = [[0,1,0.0] for k in range(localmax)]
        new_scores[-1] = [[0,1,0.0] for j in range(localmax)]
        scores = new_scores

        new_dist = np.zeros(shape=(localmax,localmax))
        new_dist[:-1,:-1] = dist
        new_dist[-1] = [1/(i+1) for i in range(localmax)] #gives higher probability to lower (easier) numbers initially to be nice
        new_dist[:,-1] = [1/(i+1) for i in range(localmax)]
        dist = new_dist

        print(colour.PURPLE + "upper bound now " +  str(localmax-1) + colour.END)

    x_dist = np.sum(dist, axis=0)
    x = np.random.choice(np.arange(0, localmax), p=x_dist/np.sum(x_dist))
    y_dist = dist[y]
    y = np.random.choice(np.arange(0, localmax), p=y_dist/np.sum(y_dist))
    ans = get_sum(x,y)


if path_bool:
    file = open(spath, "w+")
    for i in range(localmax):
        file.write(str(i))
        for k,j in scores[i][:,:2]:
            file.write(" " + str(int(k)) + "_"+ str(int(j)))
        file.write('\n')

    grand_total = int(total)+local_total
    file.write("total " + str(grand_total) + " " + str(localmax) + "\n")
    file.close()

print(colour.WARNING + "initial highpoint was " +  str(maxx-1))
print(colour.GREEN + "you ended at " +  str(localmax - 1) + colour.END)
print(colour.PURPLE + "goodbye" + colour.END)

