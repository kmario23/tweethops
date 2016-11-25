#Import built-in libs
import time
import argparse
import os
import sys
import json
#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
import tweepy

#Variables that contains the user credentials to access Twitter API 
access_token = "fill-in token here"
access_token_secret = "fill-in access_token_secret here"
consumer_key = "fill-in consumer_key here"
consumer_secret = "fill-in consumer_secret here"

def get_tweets_from_user_timeline(screen_name, count=200):
	"""twitter api allows only 200 most recent tweets/replies to be fetched, no matter what the count we pass as parameter."""
	tweets = api.user_timeline(screen_name, count = 300, include_rts = True)
	return tweets


def search_tweets_from_twitter_home(query, max_tweets, from_date, to_date):
	####searching from twitter search home #####
	searched_tweets = [status._json for status in tweepy.Cursor(api.search, q=query, count=300, since=from_date, until=to_date,
                                                          result_type="mixed",
                                                          lang="en"
                                                         ).items(max_tweets)]
	return searched_tweets

if __name__ == '__main__':
	#authenticating the application
	auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

	query = 'deep learning'
	max_tweets = 500
	from_date = "2015-02-01"
	to_date = "2016-01-29"
	#searched_tweets = [status for status in tweepy.Cursor(api.search, q=query).items(max_tweets)]
	searched_tweets = search_tweets_from_twitter_home(query, max_tweets, from_date, to_date)
	#flushing it out to stdout
	for tw in searched_tweets:
		print(tw)


    #getting tweets from a specific user from his/her twitter timeline, if the account is public.
	screen_name = 'danieltosh'
	tweet_count = 200
	user_tweets = get_tweets_from_user_timeline(screen_name, tweet_count)

    #flushing it out to stdout
    for status in user_tweets:
    	print(status._json)