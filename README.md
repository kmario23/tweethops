#To run the code, you need the access tokens & keys, which you'll get from twitter-application

##to run the code, from the terminal##
python twitter_streaming.py > ../data/twitter_stream.txt

##for keeping track of time,## will work in *nix based-distros##
time python twitter_streaming.py > ../data/twitter_stream.txt

*Rarely it may throw an error. Don't fret. 
*It simply means that our network is not fast enough to collect/fetch the data that twitter server is sending.

##to run fetch_analyse_tweet.py
##'to' date should be current day, to get the full tweets
python fetch_stale_tweets.py -q "mars mission" -o "data/search_results_new.txt" -cnt 100 -from "2015-12-31" -to "2016-4-11"

##to run scatterPlotUserStatistics.py
python scatterPlotUserStatistics.py -i ../data/user_statistics.txt

##to run scatterPlot_groupAssign.py
##Group the data points into the respective grids and assign group IDs
python scatterPlot_groupAssign.py -i ../data/user_statistics_mars-mission.txt


##to fetch (upto 100) retweets of a particular tweet, if it has any, using the 'tweet id'
Refer "get_retweets" function in "hop_level1_algorithm.py"

##to get all the followers of a particular user
python get_followers_names.py

##alternate method for getting followers
python fetch_followers.py

##run hop-algorithm implementation
python complete_hop_algorithm.py -q "Mars Mission" -cnt 2000 -from "2015-12-31" -to "2016-10-30" -o "full_results.txt"

