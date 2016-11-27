#!/usr/bin/env python
from __future__ import print_function
from __future__ import division

"""
Modified on Tue Nov 20 00:08:31 2016
@author: mario
"""
"""module for fetching friends(i.e. following) of a twitter user"""

import time
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
    print("  Friends call: Sleep for ", to_mins, "mins & continue ...\n")
    time.sleep(secs)  # well, sleep for n secs and then proceed.


def get_friends_ids(scr_name, cum_call_count):
    """
    To get ids of all friends, of a particular user.
    """
    print("getting ids of friends(following) of ", scr_name)
    frnd_call = 1
    # try 10 times to run this
    for attempt in range(10):
        try:
            ids = []
            page_count = 0
            for page in tweepy.Cursor(api.friends_ids, id=scr_name, count=5000).pages():
                page_count += 1
                print(' Getting page {} for friends ids'.format(page_count))
                ids.extend(page)
                if len(page) == 5000:
                    print(" more than 5K friends ...")
                    if (frnd_call + cum_call_count) < 13:  # avoid RateLimitExceeded Error
                        frnd_call += 1
                        sleeper(30)
                    else:
                        sleeper(960)
                        frnd_call = 1
                        cum_call_count = 0
            print("Returning ids len: ", len(ids), " friend_call_request: ", frnd_call)
            return (ids, frnd_call)
        except (tweepy.error.TweepError, tweepy.error.RateLimitError) as twerr:
            print("Error occurred: {0}".format(twerr))
            if int(twerr.api_code) == 88:
                print("Rate limit exceeded")
                sleeper(1000)
                frnd_call = 1
                cum_call_count = 0
            else:
                print("Reconnecting... after 20 secs")
                sleeper(20)
    else:
        """on failing all retries, return this"""
        return (None, frnd_call)


if __name__ == '__main__':
    user_name = 'nlprocessor'
    cum_call = 0
    user_objects, ccount = get_friends_ids(user_name, cum_call)

    for uname in user_objects:
        print(uname)
    print(len(user_objects))

