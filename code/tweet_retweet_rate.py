# -*- coding: utf-8 -*-
"""
Modified on Tue Nov 20 00:08:31 2016
@author: mario
"""

#!/usr/bin/env python
from __future__ import print_function
from __future__ import division

import os
import sys
import json
import time
import argparse
from ast import literal_eval
from email.utils import parsedate_tz
from datetime import datetime, timedelta

from multiprocessing import Process, Queue

import tweepy

# user credentials to access Twitter API
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""
CONSUMER_KEY = ""
CONSUMER_SECRET = ""

auth = tweepy.auth.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


def sleeper(secs):
    """To obey twitter API request limit.
    To be called when the request limit exceeds allowed limits (15/15min or 180/15min).
    """
    to_mins = round(secs/60.0, 3)
    print("PR1: Re/Tweet Rate Call: Sleep for ", to_mins, "mins & continue ...")
    time.sleep(secs) # well, sleep for n secs and then proceed.


def to_datetime(created_at):
    """ Input  : 'Sat Apr 23 08:11:25 +0000 2000'
        Output : datetime.datetime(2000, 4, 23, 8, 11, 25)
    """
    time_tuple = parsedate_tz(created_at.strip())
    dt = datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])


def search_tweets_from_twitter_home(query, max_tweets, from_date, to_date):
    """Method-2: searching from twitter search home. "result_type=mixed" means
                 both 'recent' & 'popular' tweets will be returned in search results.
                 returns the generator (for memory efficiency)
    """
    print("searching twitter for relevant tweets now...")
    searched_tweets = ( status._json for status in tweepy.Cursor(api.search, q=query, count=300, since=from_date, until=to_date,
                                                          result_type="mixed",
                                                          lang="en"
                                                         ).items(max_tweets) )
    return searched_tweets


def extract_user_details_from_tweets(inputfile):
    """extracts useful user & tweet details from tweets;
       returns a set of tuples (usernames, followers count), to avoid duplicate usernames
    """
    with open(inputfile, 'r') as fh:
        set_of_tuples_users = set()
        for line in fh:
            tweet = literal_eval(line)
            set_of_tuples_users.add( (tweet['user']['screen_name'], tweet['user']['followers_count'], tweet['user']['friends_count']) )
        return set_of_tuples_users


def get_tweets_from_user_timeline(screen_name, tweet_count):
    """twitter api allows only 200 most recent tweets/replies to be fetched, no matter what the count we pass as parameter."""
    user_tweets = api.user_timeline(screen_name, count = tweet_count, include_rts = True, exclude_replies = True)
    return user_tweets


def simple(arg1, cnt):
    return "Mario!!"


def present_output(usernames_set, QUERY, user_batch):
    """calculates the difference between two twitter date format.
       returns result as number of days.
    Finally return the required fields => (username, #followers, #following, #tweet-rate, #retweet-rate)
    """
    #print("{0: <30} | {1: <18} | {2: <8} | {3: <8} | {4: <8} | {5: <8} | {6: <8} | {7: <8} | {8: <8} | {9: <8}".format( \
    #      'Search Query', 'Username', 'Followrs', 'Frnds', 'Twt-cnt', 'Twt-span', 'Twt-rate', 'Rtwt-cnt', 'Rtwt-span' , 'Rtwt-rate') \
    #      )
    #print("*"*150)

    rates_dict = {}

    #calculate tweet & retweet-counts
    for idx, tl_file in enumerate(user_batch):
        handle = os.path.splitext(os.path.basename(tl_file))[0] #get twitter handle from filename since it's saved with screen_name

        for tupl in usernames_set:
            if tupl[0] == handle:
                followers, following = tupl[1], tupl[2]
                break #stop searching once match is found. The match is unique since user_details is a set.

        #initialize variables for needed fields
        tweet_count = retweet_count = 0
        tweet_rate = retweet_rate = 0.0
        all_tweet_dates = []
        all_retweet_dates = []

        with open(tl_file, 'r') as fh:
            for line in fh:
                tweet = literal_eval(line)
                if(tweet['text'].startswith('RT')):
                    all_retweet_dates.append(tweet['created_at'])
                    retweet_count += 1
                elif(not tweet['text'].startswith('RT')):
                    all_tweet_dates.append(tweet['created_at'])
                    tweet_count += 1

        #for some accounts, tweet dates list might be empty since they just don't tweet at all
        if len(all_tweet_dates) != 0:
            recentTweetAt = all_tweet_dates[0]
            oldestTweetAt = all_tweet_dates[-1]
            dtr = to_datetime(recentTweetAt)
            dto = to_datetime(oldestTweetAt)
            tweeted_days = dtr - dto                #5 days, 2:03:55

            #to avoid division-by-zero (for some users, all tweets fall on the same day or there's only 1 tweet)
            if int(tweeted_days.days) == 0:
                twt_timedelta = 1.0
            elif int(tweeted_days.days) != 0:
                twt_timedelta = int(tweeted_days.days)  #extract only number of days to calculate rate.

            #finally, tweet rate rounded to 3 decimal digits
            tweet_rate = round(tweet_count/twt_timedelta, 3)
            #print("recent tweet at ", dtr)
            #print("oldest tweet at ", dto)
        else:
            tweeted_days = -9999
            twt_timedelta = -9999
            tweet_rate = round(tweet_count/twt_timedelta, 3)
            ###print('No recent tweets available')

        #for some accounts, retweet dates list might be empty since they just don't retweet at all
        if len(all_retweet_dates) != 0:
            recentRetweetAt = all_retweet_dates[0]
            oldestRetweetAt = all_retweet_dates[-1]
            dtr = to_datetime(recentRetweetAt)
            dto = to_datetime(oldestRetweetAt)
            retweeted_days = dtr - dto         #2 days, 2:02:25

            #to avoid division-by-zero (for some users, all retweets fall on same day or there's only 1 retweet)
            if int(retweeted_days.days) == 0:
                rtwt_timedelta = 1.0
            elif int(retweeted_days.days) != 0:
                rtwt_timedelta = int(retweeted_days.days)    #extract only number of days to calculate rate.

            #finally, retweet rate rounded to 3 decimal digits
            retweet_rate = round(retweet_count/rtwt_timedelta, 3)
            #print("recent retweet at ", dtr)
            #print("oldest retweet at ", dto)
        else:
            retweeted_days = -9999
            rtwt_timedelta = -9999
            retweet_rate = round(retweet_count/rtwt_timedelta, 3)
            ####print('No recent retweets available')


        #print("{0: <30} | {1: <18} | {2: <8} | {3: <8} | {4: <8} | {5: <8} | {6: <8} | {7: <8} | {8: <8} | {9: <8}".format( \
        #      handle, followers, following, tweet_count, twt_timedelta, tweet_rate, retweet_count, rtwt_timedelta, retweet_rate ) \
        #     )
        rates_dict[handle] = (tweet_count, tweet_rate, retweet_count, retweet_rate)
        #write to file for further analysis
        with open('../data/user_statistics.txt', 'a') as fh:
            fh.write("{0: <30} | {1: <18} | {2: <8} | {3: <8} | {4: <8} | {5: <8} | {6: <8} | {7: <8} | {8: <8} | {9: <8}\n".format( \
                     QUERY, handle, followers, following, tweet_count, twt_timedelta, tweet_rate, retweet_count, rtwt_timedelta, retweet_rate ) \
                    )

    user_batch[:] = [] #needs to be empty once the process wakes up and starts querying tweets for next batch(i.e. next 15 usernames)
    return rates_dict


def compute_timeline_stats(usernames_set, QUERY, consumed_reqs):
    """INPUT: set of usernames. Eg. {('shayvj', 283, 366), ('jois', 1537, 742)}

    make API requests and get the most recent 200 timeline tweets for all these accounts.
    When API request reaches 15, sleep 15 mins to obey twitter API call limit, and then continue.
    Finally write the timeline tweets to filenames named after screen names.
    """
    TWEETS_TO_FETCH = 300
    api_requests = 0
    user_batch = []
    del user_batch[:]
    timeline_stats = {}

    for attempt in range(10):
        try:
            if api_requests < 16 and consumed_reqs < 16:
                for item in usernames_set:      # {('shayvj', 283, 366), ('jois', 1537, 742)}
                    api_requests += 1
                    consumed_reqs += 1
                    twitter_handle = item[0]
                    print(' PR1: querying timeline of ', twitter_handle)
                    #make an API request and get tweets from timeline of all users, if the account is public
                    user_tweets = get_tweets_from_user_timeline(twitter_handle, TWEETS_TO_FETCH)
                    # print(counter,") queried the timeline tweets of '", twitter_handle, "'")

                    #write timeline tweets to file
                    timeline_tweets = "../data/user_timelines/" + twitter_handle + ".txt"
                    user_batch.append(timeline_tweets)  #needed in present_output()
                    with open(timeline_tweets, 'w') as fw:
                        for status in user_tweets:
                            fw.write(str(status._json) + "\n")

                    #check for limit not exceeded
                    if api_requests < 16 and consumed_reqs < 16:
                        continue
                    else:
                        api_requests = consumed_reqs = 0
                        print('\n Updating the user statistics now... \n')
                        timeline_dict = present_output(usernames_set, QUERY, user_batch)
                        timeline_stats.update(timeline_dict)
                        del user_batch[:]
                        sleeper(910)

                else:
                    # once for loop completes, this runs
                    # for usernames < 15, directly compute the rates
                    tline_dict = present_output(usernames_set, QUERY, user_batch)
                    timeline_stats.update(tline_dict)

                    #check whether tweet rate is available for all inputs
                    inp_usernames = {item[0] for item in usernames_set}
                    avail_usernames = {item for item in timeline_stats}
                    #miss_usernames_set = {item for item in usernames_set if item[0] not in avail_usernames}
                    if len(avail_usernames) == len(inp_usernames):
                        print("\n Returning timeline stats dict...\n")
                        return (timeline_stats, consumed_reqs, True)
            else:
                api_requests = consumed_reqs = 0
                print('\n Updating the user statistics now... \n')
                timeline_dict = present_output(usernames_set, QUERY, user_batch)
                timeline_stats.update(timeline_dict)
                del user_batch[:]
                sleeper(980)

        except tweepy.error.TweepError as twerr:
            print("PR1: Error occurred: {0}".format(twerr))
            print("PR1: Reconnecting... after 30secs")
            sleeper(30)
    else:
        # on failing all attempts, run this
        return (timeline_stats, consumed_reqs, True)


def construct_graphs():
    """ Build graphs using graph-tool from the extracted retweets, favorites, retweet rate"""
    pass


if __name__ == '__main__':

    #parse command line arguments & get output filename, tweet count, from date, to date
    parser = argparse.ArgumentParser()
    requiredArgs = parser.add_argument_group('must need arguments')
    requiredArgs.add_argument('-q', '--query', help='Query for searching the tweets', required=True)
    requiredArgs.add_argument('-cnt', '--tweet_count', help='number of tweets to be returned in the result', required=True)
    requiredArgs.add_argument('-from', '--from_date', help='YYYY-MM-DD; from-date when the tweets were tweeted', required=True)
    requiredArgs.add_argument('-to', '--to_date', help='YYYY-MM-DD; to-date when the tweets were tweeted', required=True)
    requiredArgs.add_argument('-o', '--output_file', help='Output txt file to write returned tweets', required=True)
    args = parser.parse_args()

    filepath = os.getcwd() + os.path.sep + args.output_file
    if os.path.exists(filepath):
        sys.exit("output file already exists; Give new filename!")
    else:
        #create an empty file
        open(args.output_file,'a').close()

    #keyphrase to search, from & to-date in which tweets need to be returned
    query      = args.query
    max_tweets = int(args.tweet_count)
    from_date  = args.from_date
    to_date    = args.to_date

    searched_tweets = search_tweets_from_twitter_home(query, max_tweets, from_date, to_date)

    #flush out generator content to stdout
    #for tw in searched_tweets:
    #    print(tw)

    #write to output file
    with open(args.output_file, 'a') as ofile:
        for tw in searched_tweets:
            ofile.write(str(tw) + "\n")
    print("successfully written the results to file: ", args.output_file)

    #processing the tweets starts from this point
    search_results_file = args.output_file
    user_details = extract_user_details_from_tweets(search_results_file)
    print("extracted, ", len(user_details)  ," unique twitter handles from obtained twitter search results")
    print("usernames set is: ", user_details)

    #main stuff happens here
    compute_timeline_stats(user_details, consumed_requests=0)

