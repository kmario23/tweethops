#!/usr/bin/env python
from __future__ import print_function
from __future__ import division

"""
Modified on Tue Nov 20 00:08:31 2016
@author: mario
"""
"""another module for fetching followers of a twitter user"""

import time
import math

import tweepy

#user credentials to access Twitter API
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
    
auth = tweepy.auth.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


def sleeper(secs):
    """To obey twitter API request limit.
       To be called when the request limit exceeds the allowed limits (15/15min or 180/15min).
    """
    to_mins = round(secs/60.0, 3)
    print(" Followers Call: Sleep for ", to_mins, "mins & continue ...\n")
    time.sleep(secs) #well, sleep for n secs and then proceed.


def get_followers_ids(scr_name, cum_call_count):
    """ to get ids of all followers, of a particular user. """
    print("getting ids of followers of ", scr_name)
    fol_call = 1
    # try 10 times to run this
    for attempt in range(10):
        try:
            ids = []
            for page in tweepy.Cursor(api.followers_ids, screen_name=scr_name).pages():
                ids.extend(page)
                if len(page) == 5000:
                    print(" more than 5K followers ...")
                    if (fol_call + cum_call_count) < 15:  #avoid RateLimitExceeded Error
                        fol_call += 1
                        sleeper(30)
                    else:
                        sleeper(960)
                        fol_call = 1
                        cum_call_count = 0
            return (ids, fol_call)
        except (tweepy.error.TweepError, tweepy.error.RateLimitError) as twerr:
            print("Error occurred: {0}".format(twerr))
            if int(twerr.api_code) == 88:
                print("Rate limit exceeded")
                sleeper(1000)
                fol_call = 1
                cum_call_count = 0
            else:
                print("Reconnecting... after 20secs")
                sleeper(20)
    else:
        """On failing all retries, return this"""
        return (ids, 14)


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


def write_to_file(unames_list, user_name, prepend_path):
    """ Write the usernames, one per line, to a plain text file """
    with open(prepend_path + user_name + '_followers_names.txt', 'w') as out_fh:
        for name in unames_list:
            out_fh.write(name + "\n")

if __name__ == '__main__':
    scrn_name = 'nlprocessor'
    fol_ids = get_followers_ids(scrn_name)
    print(" Fetched {} (followers') twitter ids ..".format(len(fol_ids)))
    unames = get_user_names(fol_ids)
    write_to_file(unames, scrn_name, '../../data/followers/')

