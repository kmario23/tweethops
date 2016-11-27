#!/usr/bin/env python
"""Displaying the "Hops" from results from "complete_hop_algorithm.py
Completely offline processing of the data. No API requests necessary.

{AUTHOR: kmario23(https://twitter.com/nlprocessor)}

sample:
+------+---------------+---------------------+--------+-----------+----------------------+--------+-------+--------+----------+-----------+
| S.No |     UserID    |      Re/TwtTime     | Retwts | Orig.Twt? |      Dir.Folwr?      | #Folwr | #Twts | #Frnds | twt_rate | rtwt_rate |
+------+---------------+---------------------+--------+-----------+----------------------+--------+-------+--------+----------+-----------+
|  1   |   FWISD_PLTW  | 2016-11-16 14:37:09 |   3    |    Yes    |          No          |   55   |   77  |   14   |   0.44   |   0.248   |
|  2   | DirectorSciFW | 2016-11-16 16:10:02 |   -    |     No    |          1           |  459   |  1711 |  705   |  2.111   |   7.476   |
|  3   | FWISD_Science | 2016-11-16 16:19:55 |   -    |     No    |          1           |  183   |  885  |   71   |   0.5    |   5.469   |
|  4   | KAlexanderPLI | 2016-11-18 01:35:06 |   -    |     No    | (2, 'DirectorSciFW') |  113   |  2057 |   35   |  0.316   |   5.706   |
+------+---------------+---------------------+--------+-----------+----------------------+--------+-------+--------+----------+-----------+
"""

from __future__ import print_function
from __future__ import division

# built-in libs
import os
import sys
import time
import argparse
import pickle
from ast import literal_eval
from collections import defaultdict

from prettytable import PrettyTable


def do_unpickle(in_file):
    """have to call multiple times till we get EOFError
    This is because unpickling once will just give only one object {dict}.
    """

    field_names = ["Sno", "Username", "Src-Group", "#Folrs-Src", "Trgt-Group", "#Folrs-Trgt", "Orig-TwtTime", "Src-Time", "Trgt-Time"]
    tab = PrettyTable(field_names)
    tab.padding_width = 1

    finished = False
    with open(in_file, 'rb') as fh:
        sno = 0
        while not finished:
            hop_stats_list = []
            del hop_stats_list[:]  #initial cleaning
            try:
                unserialized = pickle.load(fh)
                #print("unserialized: ", unserialized, "\n")
                for key, val in unserialized.items():
                    for k, v in val.items():
                        if v[4] != "Yes":               # skip if it's "tweet row" as it's the origin
                            if type(v[5]) == int:
                                predecessor = val[v[5]]
                                #source
                                follower_cnt, rtwt_rate = predecessor[6], predecessor[10]
                                folr_src = follower_cnt
                                time_src = predecessor[2]
                                grp_src = determine_group(rtwt_rate, folr_src)
                                print("Name, SRC_RT_rate, SRC_folrs, GRP:", predecessor[1], "->", \
                                      rtwt_rate, "->", follower_cnt, "->", grp_src)
                                #target
                                follower_cnt, rtwt_rate = v[6], v[10]
                                folr_trg = follower_cnt
                                time_trg = v[2]
                                grp_trg = determine_group(rtwt_rate, folr_trg)
                                print("Name, TRG_RT_rate, TRG_folrs, GRP:", v[1], "->", \
                                      rtwt_rate, "->", folr_trg, "->", grp_trg, "\n")
                                sno += 1
                                hop_stats_list.append([sno, v[1], grp_src, folr_src, grp_trg, folr_trg, "UUUU", time_src, time_trg])
                            elif type(v[5]) == tuple:
                                if v[5][0] == 0:        # (0, 'Unknown') case; So, skip it.
                                    pass
                                else:
                                    predecessor = val[v[5][0]]
                                    #source
                                    follower_cnt, rtwt_rate = predecessor[6], predecessor[10]
                                    folr_src = follower_cnt
                                    time_src = predecessor[2]
                                    grp_src = determine_group(rtwt_rate, folr_src)
                                    print("Name, SRC_RT_rate, SRC_folrs, GRP:", predecessor[1], "->", \
                                          rtwt_rate, "->", follower_cnt, "->", grp_src)
                                    #target
                                    follower_cnt, rtwt_rate = v[6], v[10]
                                    folr_trg = follower_cnt
                                    time_trg = v[2]
                                    grp_trg = determine_group(rtwt_rate, folr_trg)
                                    print("Name, TRG_RT_rate, folrs, GRP:", v[1], "->", \
                                          rtwt_rate, "->", folr_trg, grp_trg, "\n")
                                    sno += 1
                                    hop_stats_list.append([sno, v[1], grp_src, folr_src, grp_trg, folr_trg, "UUUU", time_src, time_trg])
                        elif(v[4] == 'Yes'):
                            # get original tweet time
                            orig_tweet_time = v[2]

                    if len(hop_stats_list):
                        #update original time
                        for lis in hop_stats_list:
                            lis[6] = orig_tweet_time

                        #add to prettytable
                        for lis in hop_stats_list:
                            tab.add_row(lis)
            except EOFError:
                finished = True
                print(tab)
                break


def determine_group(rrate, folrs):
    """resolve to which group does a "retweet_rate" and "followers_count" belong to.
    # retweet rate is considered here
    # numbers in range is +1, to use 'range' correctly

    GROUP DEFINITION:
        {
        G1: (rrate <= 1 &  #folrs >= 100)
        G2: (rrate <= 1 &  #folrs < 100)
        G3: (1 < rrate <= 10 and folrs < 200)
        G4: (10 < rrate <= 50 & #folrs < 100)
        G5: (2 <= rrate < 10 & #folrs >= 200)
        G6: (10 < rrate < 50 & 100 <= #folrs < 1000)
        G7: (rrate > 50 & #folrs < 200)
        G8: (10 < rrate <= 50 & #folrs >= 1000)
        G9: (rrate > 50 & 200 <= #folrs < 8000)
        G10: (rrate > 50 &  #folrs >= 8000)
        }
    """

    rrate = round(abs(rrate))
    if(rrate <= 1 and folrs >= 100):  # G1
        return "G1"
    elif(rrate <= 1 and folrs < 100): # G2
        return "G2"
    elif(rrate > 50 and folrs < 200):  # G7
        return "G7"
    elif(rrate > 50 and folrs >= 8000): # G10
        return "G10"
    elif(rrate in range(11, 51) and folrs in range(100, 1000)):     # G6
        return "G6"
    elif(rrate > 50 and folrs in range(200, 8000)):     # G9
        return "G9"
    elif(rrate in range(2, 11) and folrs < 200):        # G3
        return "G3"
    elif(rrate in range(11, 51) and folrs < 100):       # G4
        return "G4"
    elif(rrate in range(2, 11) and folrs >= 200):       # G5
        return "G5"
    elif(rrate in range(11, 51) and folrs >= 1000):       # G8
        return "G8"


if __name__ == '__main__':
    # parse command line arguments & get input filename
    parser = argparse.ArgumentParser()
    requiredArgs = parser.add_argument_group('must need arguments')
    requiredArgs.add_argument('-input', '--input_file', help='pickle file', required=True)
    args = parser.parse_args()

    in_file = args.input_file

    do_unpickle(in_file)

