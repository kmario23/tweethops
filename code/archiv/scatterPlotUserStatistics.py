# -*- coding: utf-8 -*-
"""
Modified on Tue Apr 12 19:11:31 2016

@author: mario
"""

#!/usr/bin/env python
from __future__ import print_function
import argparse

import numpy as np
import matplotlib.pyplot as plt


def scatter_plot(inputfile):
    """ input: takes user statistics file which has followers, following, tweet-retweet rate numbers
        Output: generates a scatter plot (grid)
    """

    followers_count = []
    tweet_retweet_rates = []

    with open(inputfile, 'r') as fh:
        for line in fh:
            split_list = line.strip().split('|')  #split(sep='|') in python3
            fc = int(split_list[2].strip())

            #convert the figures to log scale #use log10 for standard base 10
            followers_count.append( round(np.log(fc), 3) )
            trr = float(split_list[6].strip()) + float(split_list[9].strip())

            #convert the figures to log scale #use log10 for standard base 10
            tweet_retweet_rates.append( round(np.log(trr),3) )

    #construct objects in the background
    plt.scatter(tweet_retweet_rates, followers_count, label='rate vs. followers', color='g', marker='*', s=100) #s for size
    plt.xlabel('tweet-retweet-rate/day (ln scale)')
    plt.ylabel('followers count (ln scale)')

    plt.title('Twitter Usage Statistics of Users') #graph title
    plt.legend(loc=2) #code for upper right, left is 1,2 resp. lower left, right is 3,4 resp.
    plt.grid(True)    #to show the grid layout

    #finally show everything
    plt.show()


if __name__ == '__main__':
    #parse command line arguments & get filename
    parser = argparse.ArgumentParser()
    requiredArgs = parser.add_argument_group('must need arguments')
    requiredArgs.add_argument('-i', '--input_file', help='Input txt file', required=True)
    args = parser.parse_args()

    scatter_plot(args.input_file)
