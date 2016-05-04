# -*- coding: utf-8 -*-
"""
Modified on Tue May 2 02:22:31 2016

@author: mario
"""

#!/usr/bin/env python
from __future__ import print_function
import argparse
import collections
import re

import numpy as np
import matplotlib.pyplot as plt



def assignGroup_Id(user_stats_dict):
    """input: takes user statistics file which has followers, following, tweet-retweet rate numbers
       output: Assigns a group ID to each (user) data-point (ln scale)
    """
    #define constant grid size of (2x2) square, with group IDs
    wholegrid = {
                 'G01' : [(-6.0, -4.0), (-2.0, 0.0)],
                 'G02' : [(-4.0, -2.0), (-2.0, 0.0)],
                 'G03' : [(-2.0,  0.0), (-2.0, 0.0)],
                 'G04' : [( 0.0,  2.0), (-2.0, 0.0)],
                 'G05' : [( 2.0,  4.0), (-2.0, 0.0)],
                 'G06' : [( 4.0,  6.0), (-2.0, 0.0)],

                 'G07' : [(-6.0, -4.0), (0.0, 2.0)],
                 'G08' : [(-4.0, -2.0), (0.0, 2.0)],
                 'G09' : [(-2.0,  0.0), (0.0, 2.0)],
                 'G10' : [( 0.0,  2.0), (0.0, 2.0)],
                 'G11' : [( 2.0,  4.0), (0.0, 2.0)],
                 'G12' : [( 4.0,  6.0), (0.0, 2.0)],

                 'G13' : [(-6.0, -4.0), (2.0, 4.0)],
                 'G14' : [(-4.0, -2.0), (2.0, 4.0)],
                 'G15' : [(-2.0,  0.0), (2.0, 4.0)],
                 'G16' : [( 0.0,  2.0), (2.0, 4.0)],
                 'G17' : [( 2.0,  4.0), (2.0, 4.0)],
                 'G18' : [( 4.0,  6.0), (2.0, 4.0)],

                 'G19' : [(-6.0, -4.0), (4.0, 6.0)],
                 'G20' : [(-4.0, -2.0), (4.0, 6.0)],
                 'G21' : [(-2.0,  0.0), (4.0, 6.0)],
                 'G22' : [( 0.0,  2.0), (4.0, 6.0)],
                 'G23' : [( 2.0,  4.0), (4.0, 6.0)],
                 'G24' : [( 4.0,  6.0), (4.0, 6.0)],

                 'G25' : [(-6.0, -4.0), (6.0, 8.0)],
                 'G26' : [(-4.0, -2.0), (6.0, 8.0)],
                 'G27' : [(-2.0,  0.0), (6.0, 8.0)],
                 'G28' : [( 0.0,  2.0), (6.0, 8.0)],
                 'G29' : [( 2.0,  4.0), (6.0, 8.0)],
                 'G30' : [( 4.0,  6.0), (6.0, 8.0)],

                 'G31' : [(-6.0, -4.0), (8.0, 10.0)],
                 'G32' : [(-4.0, -2.0), (8.0, 10.0)],
                 'G33' : [(-2.0,  0.0), (8.0, 10.0)],
                 'G34' : [( 0.0,  2.0), (8.0, 10.0)],
                 'G35' : [( 2.0,  4.0), (8.0, 10.0)],
                 'G36' : [( 4.0,  6.0), (8.0, 10.0)],

                 'G37' : [(-6.0, -4.0), (10.0, 12.0)],
                 'G38' : [(-4.0, -2.0), (10.0, 12.0)],
                 'G39' : [(-2.0,  0.0), (10.0, 12.0)],
                 'G40' : [( 0.0,  2.0), (10.0, 12.0)],
                 'G41' : [( 2.0,  4.0), (10.0, 12.0)],
                 'G42' : [( 4.0,  6.0), (10.0, 12.0)],

                 'G43' : [(-6.0, -4.0), (12.0, 14.0)],
                 'G44' : [(-4.0, -2.0), (12.0, 14.0)],
                 'G45' : [(-2.0,  0.0), (12.0, 14.0)],
                 'G46' : [( 0.0,  2.0), (12.0, 14.0)],
                 'G47' : [( 2.0,  4.0), (12.0, 14.0)],
                 'G48' : [( 4.0,  6.0), (12.0, 14.0)],

                 'G49' : [(-6.0, -4.0), (14.0, 16.0)],
                 'G50' : [(-4.0, -2.0), (14.0, 16.0)],
                 'G51' : [(-2.0,  0.0), (14.0, 16.0)],
                 'G52' : [( 0.0,  2.0), (14.0, 16.0)],
                 'G53' : [( 2.0,  4.0), (14.0, 16.0)],
                 'G54' : [( 4.0,  6.0), (14.0, 16.0)],
                }

    assignedGroups = collections.defaultdict(float)

    for key, val in user_stats_dict.items():
        username = key
        fcount = round(np.log(val[0]), 3)
        trrate = round(np.log(val[1]), 3)

        for k, v in wholegrid.items():
            xlow = v[0][0]  #4.0 in [(4.0, 6.0), ...]
            xupp = v[0][1]  #6.0 in [(4.0, 6.0), ...]
            ylow = v[1][0]  #14.0 in [(14.0, 16.0), ...]
            yupp = v[1][1]  #16.0 in [(14.0, 16.0), ...]
            #print(xlow, trrate, xupp, ylow, fcount, yupp)
            
            if xlow <= trrate < xupp and ylow <= fcount < yupp:
                if k not in assignedGroups:
                    assignedGroups[k] = [ username + str((trrate, fcount)) ]
                else:
                    assignedGroups[k].append( username + str((trrate, fcount)) )

    return (assignedGroups, wholegrid)

def scatter_plot(user_dict):
    """ input: takes user statistics file which has followers, following, tweet-retweet rate numbers
        Output: generates a scatter plot (grid)
    """

    followers_count = []
    tweet_plus_retweet_rate = []
    
    for key, val in user_dict.items():
            #convert the figures to log scale #use log10 for standard base 10
            followers_count.append( round(np.log(val[0]), 3) )
            tweet_plus_retweet_rate.append( round(np.log(val[1]),3) )
    
    #construct objects in the background
    plt.scatter(tweet_plus_retweet_rate, followers_count, label='rate vs. followers', color='g', marker='*', s=100) #s for size
    plt.xlabel('tweet+retweet--rate/day (ln scale)')
    plt.ylabel('followers count (ln scale)')
    
    plt.title('Twitter Usage Statistics of Users') #graph title
    plt.legend(loc=2) #code for upper right, left is 1,2 resp. lower left, right is 3,4 resp.
    plt.grid(True)    #to show the grid layout
    
    #axes = plt.gca()
    #axes.set_xlim([-1.0, 10])
    #axes.set_ylim([0.0, 20])
    
    #finally show everything
    plt.show()


if __name__ == '__main__':
    #parse command line arguments & get filename
    parser = argparse.ArgumentParser()
    requiredArgs = parser.add_argument_group('must need arguments')
    requiredArgs.add_argument('-i', '--input_file', help='Input txt file', required=True)
    args = parser.parse_args()
    
    #read user statistics into a dict; {'CNBC': (2311199, 200)} #follower_cnt, tw+rwt rate
    user_stats_dict = {}
    with open(args.input_file, 'r') as fh:
        for line in fh:
            split_list = line.strip().split('|')  #split(sep='|') in python3
            uname = str(split_list[1].strip())
            fc = int(split_list[2].strip())
            trr = float(split_list[6].strip()) + float(split_list[9].strip())
    
            #key: username, value: (follower, twt-rtwt-rate) raw scores
            user_stats_dict[uname] = (fc, trr)

    (groups, grid) = assignGroup_Id(user_stats_dict)
    for k, v in groups.items():
        print(k, grid[k], '=>', v, "\n")

    scatter_plot(user_stats_dict)