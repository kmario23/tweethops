# -*- coding: utf-8 -*-
"""
Modified on Mon Aug 15 20:58:31 2016
@author: mario
"""

#!/usr/bin/env python
"""implementation of the hop algorithm to determine tweet hops (as retweet)"""
from __future__ import print_function
from __future__ import division

#Import built-in libs
import time
import argparse
import os
import sys
from ast import literal_eval

#Import the necessary methods from tweepy library
import tweepy

#import own module
from followers import get_followers_names as gfn

#user credentials to access Twitter API
ACCESS_TOKEN = "INSERT TOKEN HERE"
ACCESS_TOKEN_SECRET = "INSERT TOKEN HERE"
CONSUMER_KEY = "INSERT TOKEN"
CONSUMER_SECRET = "INSERT TOKEN"


def sleeper(secs):
    """To obey twitter API request limit.
       To be called when the request limit exceeds the allowed limits (15/15min or 180/15min).
    """
    to_mins = round(secs/60.0, 3)
    print("    Sleep for ", to_mins, "mins and continue afterwards...")
    time.sleep(secs) #well, sleep for n secs and then proceed.


def search_tweets_from_twitter_home(query, max_tweets, from_date, to_date):
    """Method-2: searching from twitter search home.
       'result_type=mixed' means both 'recent'&'popular' tweets will be returned in results.
       returns the generator (for memory efficiency)
    """
    print("searching twitter for relevant tweets now...")
    searched_tweets = (status._json for status in tweepy.Cursor(api.search,
                                                                q=query,
                                                                count=300,
                                                                since=from_date,
                                                                until=to_date,
                                                                result_type="mixed",
                                                                lang="en"
                                                               ).items(max_tweets))
    return searched_tweets


def get_retweets(tid, rwt_count):
    """Returns up to 100 of the first retweets of a given tweet.
       returns the generator (for memory efficiency)
    """
    print("\n    fetching retweets of tweet: ", tid)
    sleeper(10) #to avoid null results because of fast requests, network latency
    fetched_retweets = (status._json for status in api.retweets(tid, rwt_count))
    return fetched_retweets


def extract_user_details(inputfile):
    """extracts tweet ids from tweets;
       these ids are used to fetch all_retweets of a particular tweet.
    """
    with open(inputfile, 'r') as in_fh:
        tweet_ids_set = set()
        for line in in_fh:
            tweet = literal_eval(line)
            if tweet['retweet_count'] > 0:  #filter tweets with at least 1 retweet
                tweet_ids_set.add((tweet['user']['screen_name'], tweet['id_str']))
        return tweet_ids_set


def get_retweets_for_tweetids(twt_ids, ids_set):
    """get all retweets for a set of tweets
       INPUT : a list of tweet ids
       OUTPUT: all retweets for each tweet id
    """
    calls_count = 0
    for tid in twt_ids:
        if calls_count < 15:
            #print("    retweets of tweet id ", tid)
            calls_count += 1
            retweet_results = get_retweets(int(tid), 100)
            retweets_list = [rt for rt in retweet_results]
            print("fetched ", len(retweets_list), " retweets")

            if retweets_list:
                write_to_file(retweets_list, tid)
                retweeter_names = []
                del retweeter_names[:] #initial cleaning
                for res in retweets_list:
                    tweeter_name = res['retweeted_status']['user']['screen_name']
                    rtwtr_name = res['user']['screen_name']
                    retweeter_names.append(rtwtr_name)
                    print("retweeted by ", rtwtr_name)
                print("original tweeter username: ", tweeter_name, "\n")

                #fetch followers of original tweeter
                folr_ids = gfn.get_followers_ids(tweeter_name)
                print(" Fetched {} (followers') twitter ids ..".format(len(folr_ids)))
                screen_names = gfn.get_user_names(folr_ids)
                gfn.write_to_file(screen_names, tweeter_name, "../data/followers/")

                #compute hop
                compute_hop1_overlap(screen_names, retweeter_names, tweeter_name)
        else:
            calls_count = 0
            sleeper(1000)


def write_to_file(retweets, tid):
    """write retweets to file"""
    fname = "../data/retweets/" + str(tid) + ".txt"
    with open(fname, 'w') as rwtfile:
        for rwt in retweets:
            rwtfile.write(str(rwt) + "\n")
    print("successfully written the retweets to file: ", fname)


def compute_hop1_overlap(scr_names, retweeters, twtr_name):
    """determine overlap between user ANON's followers and
       retweeters of a particular tweet by user ANON
    """
    hop1_overlap = set(scr_names) & set(retweeters)
    print("Total retweeters: ", len(retweeters),
          "; Direct followers of ", twtr_name, ": ", len(hop1_overlap), "\n")


if __name__ == '__main__':
    #parse command line arguments & get output filename, tweet count, from date, to date
    parser = argparse.ArgumentParser()
    requiredArgs = parser.add_argument_group('must need arguments')
    requiredArgs.add_argument('-q', '--query', help='Query to be searched', required=True)
    requiredArgs.add_argument('-cnt', '--tweet_count', help='#tweets to be returned', required=True)
    requiredArgs.add_argument('-from', '--from_date', help='YYYY-MM-DD; from-date', required=True)
    requiredArgs.add_argument('-to', '--to_date', help='YYYY-MM-DD; to-date', required=True)
    requiredArgs.add_argument('-o', '--output_file', help='file for returned tweets', required=True)
    args = parser.parse_args()

    FILEPATH1 = os.getcwd() + os.path.sep + args.output_file
    if os.path.exists(FILEPATH1):
        sys.exit("output/retweets file already exists; Give new filename!")
    else:
        #creates an empty file
        open(args.output_file, 'a').close()

    #authenticating the app (https://apps.twitter.com/app/9190005)
    auth = tweepy.auth.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    #keyphrase to search, from & to-date in which tweets need to be returned
    QUERY = args.query
    MAX_TWEETS = int(args.tweet_count)
    FROM_DATE = args.from_date
    TO_DATE = args.to_date

    #searched_tweets = [status for status in tweepy.Cursor(api.search, q=query).items(max_tweets)]
    fetched_tweets = search_tweets_from_twitter_home(QUERY, MAX_TWEETS, FROM_DATE, TO_DATE)

    #write searched results(tweets) to output file
    with open(args.output_file, 'a') as ofile:
        for tw in fetched_tweets:
            ofile.write(str(tw) + "\n")
    print("successfully written the results to file: ", args.output_file)

    #offline processing of tweets starts from this point
    search_results_file = args.output_file
    twt_ids_set = extract_user_details(search_results_file)

    #get only tweet_ids
    extract_tid = lambda x: x[1]
    retweeted_tweet_ids = map(extract_tid, twt_ids_set)
    tweet_ids = list(retweeted_tweet_ids)
    print("extracted, ", len(tweet_ids), " ids from search results(tweets with atleast 1 retweet)")

    #get retweets now
    print("\ngetting retweets of tweets now... ")
    get_retweets_for_tweetids(tweet_ids, twt_ids_set)

