#!/usr/bin/env python
"""module for fetching followers of a twitter user"""
from __future__ import print_function
from __future__ import division

#Import built-in libs
import time

#Import the necessary methods from tweepy library
import tweepy

#user credentials to access Twitter API
ACCESS_TOKEN = "YOUR TOKEN HERE"
ACCESS_TOKEN_SECRET = "YOUR TOKEN HERE"
CONSUMER_KEY = "YOUR TOKEN HERE"
CONSUMER_SECRET = "YOUR TOKEN HERE"


def sleeper(secs):
    """To obey twitter API request limit.
       To be called when the request limit exceeds the allowed limits (15/15min or 180/15min).
    """
    to_mins = round(secs/60.0, 3)
    print("\n Well, I'm going to sleep for ", to_mins, " mins and will continue afterwards...\n")
    time.sleep(secs) #well, sleep for n secs and then proceed.

def get_followers(scr_name):
    """ Another method to get the followers list of a particular user """
    user_objs = tweepy.Cursor(api.followers, screen_name=scr_name).items()
    return user_objs

def write_to_file(followers_list, uname):
    """ Write the usernames, one per line, to a plain text file """
    with open('../../data/followers/'+uname+'_followers_list.txt', 'w') as out_fh:
        for fol in followers_list:
            out_fh.write(fol + "\n")


if __name__ == '__main__':
    auth = tweepy.auth.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    user_name = 'manaalfar'
    user_objects = get_followers(user_name)

    """stops after every 300 names for 15 mins, to obey API limits, and then continues..."""
    followers = []
    while True:
        try:
            user = next(user_objects)
        except tweepy.TweepError:
            write_to_file(followers, user_name)
            sleeper(960)
            user = next(user_objects)
        except StopIteration:
            break

        followers.append(user.screen_name)

