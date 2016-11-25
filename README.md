#### 1) To run the code, get the access tokens & keys from [twitter-application](https://apps.twitter.com/)

#### 2) To stream realtime tweets
    time python twitter_streaming.py > ../data/twitter_stream.txt

 > Rarely it may throw an error. Don't fret.
 > It simply means that our network is not fast enough to collect/fetch the data that twitter server is sending.

##### 3) For custom query: 'to' date should be current day to get the full tweets
    python fetch_stale_tweets.py -q "mars mission" -o "data/results.txt" -cnt 100 \
                                              -from "2015-12-31" -to "2016-11-11"

##### 4) Plot the statistics
    python scatterPlotUserStatistics.py -i ../data/user_statistics.txt

##### 5) Group the data points into the respective grids and assign group IDs
    python scatterPlot_groupAssign.py -i ../data/user_statistics_mars-mission.txt

##### 6) Run hop-algorithm implementation
---
    time python complete_hop_algorithm.py -q "mars mission" -cnt 10000 -thresh 50000 \
                                -from "2015-12-31" -to "2016-11-25" -o all_results.txt
