import json
import pandas as pd
import matplotlib.pyplot as plt

#json response file from data stream
tweets_raw_file = "../data/twitter_datastream.txt"
""" takes json response from twitter_datastream and get country of origin of tweet & language etc.,"""
tweets_list = []
tweets_fh = open(tweets_raw_file, "r")
for line in tweets_fh:
	try:
		tweet = json.loads(line)
		tweets_list.append(tweet)
	except:
		continue

print "Total tweet count is: ", len(tweets_list)
tweets_fh.close()

#empty panda dataframe
tweets = pd.DataFrame()

#extracting tweet text, language, & place of origin
tweets['text'] = map(lambda tweet: tweet.get('text'), tweets_list) #not all tweets have 'text' field #using dict get
tweets['lang'] = map(lambda tweet: tweet.get('lang'), tweets_list) #not all tweets have 'lang' field #using dict get
tweets['country'] = map(lambda tweet: tweet.get('place', {}).get('country', {}) if tweet.get('place') != None else None, tweets_list) #dict get for dict of dict

#plotting top-5 tweets languages
tweets_by_lang = tweets['lang'].value_counts()

fig, ax = plt.subplots()
ax.tick_params(axis='x', labelsize=15)
ax.tick_params(axis='y', labelsize=10)
ax.set_xlabel('Languages', fontsize=15)
ax.set_ylabel('Number of tweets' , fontsize=15)
ax.set_title('Top 5 languages', fontsize=15, fontweight='bold')
tweets_by_lang[:5].plot(ax=ax, kind='bar', color='red')
#print "Total languages is : ", len(tweets_by_lang), "\n", tweets_by_lang

#plotting top-5 place of origin of tweets
tweets_by_country = tweets['country'].value_counts()

fig, ax = plt.subplots()
ax.tick_params(axis='x', labelsize=15)
ax.tick_params(axis='y', labelsize=10)
ax.set_xlabel('Countries', fontsize=15)
ax.set_ylabel('Number of tweets' , fontsize=15)
ax.set_title('Top 5 Countries', fontsize=15, fontweight='bold')
tweets_by_country[:5].plot(ax=ax, kind='bar', color='green')
#print "Total countries is : ", "\n", tweets_by_country
plt.show()