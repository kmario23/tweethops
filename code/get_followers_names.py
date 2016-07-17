#!/usr/bin/env python
from __future__ import print_function
from __future__ import division

#Import built-in libs
import time
import math
import argparse
import os
import sys
import json

#Import the necessary methods from tweepy library
import tweepy
from tweepy import OAuthHandler

#user credentials to access Twitter API
access_token = "your access token here"
access_token_secret = "your access token secret here"
consumer_key = "your consumer key here"
consumer_secret = "your consumer secret here"


def sleeper(secs):
    """To obey twitter API request limit.
       To be called when the request limit exceeds the allowed limits (15/15min or 180/15min).
    """
    to_mins = secs/60.0
    print(" Well, I'm going to sleep for ", to_mins, " mins and will continue afterwards...\n")
    time.sleep(secs) #well, sleep for n secs and then proceed.


def get_followers_ids(scr_name):
    """first we've to get ids of all followers, of a particular user.
    """
    ids = []
    for page in tweepy.Cursor(api.followers_ids, screen_name=scr_name).pages():
        ids.extend(page)
        if len(page) == 5000:
            print(" more than 5K followers ...")
            sleeper(60)
    return ids


def get_user_names(tids):
    """Input : ids of users
       Output: screen_name of the users
       Feed the ids in list of 100s, which is the limit for users lookup
       Sleep for 30 seconds to be on the safe side
    """
    t_ids = tids[:]
    total_ids = len(tids)
    user_names = []

    passes = 1
    while len(t_ids):
        if len(t_ids) > 100:
            first_100 = t_ids[0:100]
            del t_ids[0:100]
            user_objs = api.lookup_users(user_ids=first_100)
            for user in user_objs:
                user_names.append(user.screen_name)
            print(" pass {} of {} done ...".format(passes, math.ceil(total_ids/100)))
            passes += 1
            sleeper(30)
        else:
            user_objs = api.lookup_users(user_ids=t_ids)
            del t_ids[:]
            for user in user_objs:
                user_names.append(user.screen_name)
            print(" pass {} of {} done ...".format(passes, math.ceil(total_ids/100)))
    return user_names


def write_to_file(unames_list):
    """ Write the usernames, one per line, to a plain text file
    """
    with open('../data/followers/followers_names.txt', 'w') as fh:
        for name in unames_list:
            fh.write(name + "\n")


if __name__ == '__main__':
    #APP2 (https://apps.twitter.com/app/12077936/)
    auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    user_name = 'rsalakhu'
    #user_name = 'nlprocessor'
    ids = get_followers_ids(user_name)
    print(" Fetched {} (followers') twitter ids ..".format(len(ids)))
    unames = get_user_names(ids)
    write_to_file(unames)

