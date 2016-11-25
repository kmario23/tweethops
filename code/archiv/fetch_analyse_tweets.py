# -*- coding: utf-8 -*-
"""
Modified on Mon Aug 15 21:08:31 2016
@author: mario
"""

#!/usr/bin/env python
from __future__ import print_function
from __future__ import division

#Import built-in libs
import time
import argparse
import os
import sys
import json
from datetime import datetime, timedelta
from email.utils import parsedate_tz
from ast import literal_eval

#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
import tweepy

#user credentials to access Twitter API
ACCESS_TOKEN = "INSERT TOKEN HERE"
ACCESS_TOKEN_SECRET = "INSERT TOKEN HERE"
CONSUMER_KEY = "INSERT TOKEN"
CONSUMER_SECRET = "INSERT TOKEN"


def sleeper(secs):
    print("\n I'm going to sleep for 15 mins and will continue afterwards...\n")
    time.sleep(secs) #well, sleep for 15 mins and then proceed.


def to_datetime(created_at):
    """ Input  : 'Sat Apr 23 08:11:25 +0000 2000'
        Output : datetime.datetime(2000, 4, 23, 8, 11, 25)
    """
    time_tuple = parsedate_tz(created_at.strip())
    dt = datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])


def search_tweets_from_twitter_home(query, max_tweets, from_date, to_date):
    """Method-2: searching from twitter search home.
       "result_type=mixed" means both 'recent' & 'popular' tweets will be returned in search results.
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


def extract_user_details_from_tweets(inputfile):
    """extracts useful user & tweet details from tweets;
       returns a set of tuples (usernames, followers count), to avoid duplicate usernames
    """
    with open(inputfile, 'r') as fh:
        set_of_tuples_users = set()
        for line in fh:
            tweet = literal_eval(line)
            set_of_tuples_users.add((tweet['user']['screen_name'],
                                      tweet['user']['followers_count'],
                                      tweet['user']['friends_count']))
        return set_of_tuples_users


def get_tweets_from_user_timeline(screen_name, tweet_count):
    """twitter api allows only 200 most recent tweets/replies to be fetched,
       no matter what the count we pass as parameter.
    """
    user_tweets = api.user_timeline(screen_name, count = tweet_count, include_rts = True, exclude_replies = True)
    return user_tweets


def present_output(usernames_set, user_batch):
    """calculates the difference between two twitter date format.
       returns result as number of days.
       present the required fields => (query, username, #followers, #following, #tweet-rate, #retweet-rate)
    """
    print("{0: <30} | {1: <20} | {2: <9} | {3: <9} | {4: <9} | {5: <9} | {6: <9} | {7: <9} | {8: <9} | {9: <9}".format( \
          'Search Query', 'Username', 'Followers', 'Following', 'Tweet-cnt', 'Twt_span', 'Twt_rate', 'Retwt-cnt', 'Rtwt_span' , 'Rtwt_rate') \
          )
    print("*"*150)

    #calculate tweet & retweet-counts
    for idx, tl_file in enumerate(user_batch):
        handle = os.path.splitext(os.path.basename(tl_file))[0] #get twitter handle from filename since it's saved with screen_name

        for tupl in user_details:
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


        print("{0: <30} | {1: <20} | {2: <9} | {3: <9} | {4: <9} | {5: <9} | {6: <9} | {7: <9} | {8: <9} | {9: <9}".format( \
              query, handle, followers, following, tweet_count, twt_timedelta, tweet_rate, retweet_count, rtwt_timedelta, retweet_rate ) \
             )

        #write to file for further analysis
        with open('../data/user_statistics.txt', 'a') as fh:
            fh.write("{0: <30} | {1: <20} | {2: <9} | {3: <9} | {4: <9} | {5: <9} | {6: <9} | {7: <9} | {8: <9} | {9: <9}\n".format( \
                     query, handle, followers, following, tweet_count, twt_timedelta, tweet_rate, retweet_count, rtwt_timedelta, retweet_rate ) \
                    )
    
    user_batch[:] = [] #needs to be empty once the process wakes up and starts querying tweets for next batch(i.e. next 15 usernames)
    return user_batch


def make_API_call_and_write2file(usernames_set, query):
    """ Taking set of usernames, make API requests and get the most recent 200 timeline tweets for all these accounts. 
    When API request count reaches 15, sleep for 15 mins to obey the twitter API call restriction, and then continue.
    Finally write the timeline tweets to filenames named after screen names. """

    tweets_to_fetch = 200
    api_requests = counter = 0
    user_batch = []

    for item in usernames_set:
        api_requests += 1
        counter += 1
        if api_requests < 15:
            twitter_handle = item[0]
            #make an API request and get tweets from timeline of all users, if the account is public
            user_tweets = get_tweets_from_user_timeline(twitter_handle, tweets_to_fetch)
            print(counter,") queried the timeline tweets of '", twitter_handle, "'")

            #write timeline tweets to file
            timeline_tweets = "../data/user_timelines/" + twitter_handle + ".txt"
            user_batch.append(timeline_tweets)  #needed in present_output()
            with open(timeline_tweets, 'w') as fw:
                for status in user_tweets:
                    fw.write(str(status._json) + "\n")
        else:
            api_requests = 0
            print('\n Presenting the user statistics now... \n')
            user_batch = present_output(usernames_set, user_batch)
            sleeper(secs=1000)

    #call present_output function directly if the user count is less than 15
    api_requests = counter = 0
    print('\n Presenting the user statistics now... \n')
    user_batch = present_output(usernames_set, user_batch)


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

    auth = tweepy.auth.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    #keyphrase to search, from & to-date in which tweets need to be returned
    query      = args.query
    max_tweets = int(args.tweet_count)
    from_date  = args.from_date
    to_date    = args.to_date

    #searched_tweets = [status for status in tweepy.Cursor(api.search, q=query).items(max_tweets)]
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
    
    #main stuff happens here
    make_API_call_and_write2file(user_details, query)

