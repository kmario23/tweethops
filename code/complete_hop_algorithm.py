#!/usr/bin/env python
"""implementation of the hop algorithm to determine tweet hops (as retweet)"""
from __future__ import print_function
from __future__ import division

#built-in libs
import time
import argparse
import os
import sys
from ast import literal_eval
from datetime import datetime, timedelta
from email.utils import parsedate_tz

#necessary methods from tweepy lib
import tweepy

from prettytable import PrettyTable

#import own modules
from followers import get_followers_names as gfn
from friends import get_friends_ids as gfi
import tweet_retweet_rate as get_rates

#user credentials to access Twitter API
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""
CONSUMER_KEY = ""
CONSUMER_SECRET = ""


def sleeper(secs):
    """To obey twitter API request limit.
    To be called when the request limit exceeds the allowed limits (15/15min or 180/15min).
    """
    to_mins = round(secs/60.0, 3)
    print("Main Call: Sleep for ", to_mins, "mins & continue ...")
    time.sleep(secs) #well, sleep for n secs and then proceed.


def to_datetime(created_at):
    """ Input  : 'Sat Apr 23 08:11:25 +0000 2000'
        Output : datetime.datetime(2000, 4, 23, 8, 11, 25)
    """
    time_tuple = parsedate_tz(created_at.strip())
    dt = datetime(*time_tuple[:6])
    return dt


def search_tweets_from_twitter_home(query, max_tweets, from_date, to_date):
    """Method-2: searching from twitter search home.
       'result_type=mixed' means both 'recent'&'popular' tweets will be returned in results.
       'result_type=top' is good here, since it returns tweets of tweeters having moderate followers.
       returns the generator (for memory efficiency)
    """
    print("searching twitter for relevant tweets now...")
    searched_tweets = (status._json for status in tweepy.Cursor(api.search,
                                                                q=query,
                                                                count=300,
                                                                since=from_date,
                                                                until=to_date,
                                                                result_type="top",
                                                                lang="en"
                                                               ).items(max_tweets))
    return searched_tweets


def get_retweets(tid, rwt_count):
    """Returns up to 100 of the first retweets of a given tweet.
       returns the generator (for memory efficiency)
       On Error: return empty generator
    """
    print("\nfetching retweets of tweet: ", tid)
    sleeper(10) #to avoid null results because of fast requests, network latency
    try:
        fetched_retweets = (status._json for status in api.retweets(tid, rwt_count))
        return fetched_retweets
    except tweepy.error.TweepError as twerr:
        print("Exception raised: {0}".format(twerr))
        time.sleep(10)
        return (item for item in [])


def extract_user_details(inputfile):
    """extracts tweet ids for tweets with atleast 1 retweet;
       retweets itself might be returned in search results;
       filter out those entries since retweeting a retweet increases only original tweet's retweet count;
       these ids are used to fetch all_retweets of a particular tweet.
    """
    with open(inputfile, 'r') as in_fh:
        tweet_ids_set = set()
        for line in in_fh:
            tweet = literal_eval(line)
            # filter out tweets with at least 1 retweet
            if tweet['retweet_count'] > 0 and not tweet['text'].startswith("RT @"):
                tweet_ids_set.add((tweet['user']['screen_name'], tweet['id_str'], tweet['user']['followers_count']))
        return tweet_ids_set


def get_retweets_for_tweetids(twt_ids, twtrIDmap, folr_thresh):
    """To get all retweets for a set of tweets.
       INPUT : a list of tweet ids
       OUTPUT: all retweets for each tweet id
    """
    total_calls_count = 0
    follower_calls = 0
    friends_calls = 0

    for tid in twt_ids:
        if int(twtrIDmap[tid][1]) < int(folr_thresh):               #skip tweeters with huge followers
                print("\n", twtrIDmap[tid][0],"=>", twtrIDmap[tid][1], "=>", str(folr_thresh))
                total_calls_count += 1
                retweet_results = get_retweets(int(tid), 100)
                retweets_list = [rt for rt in retweet_results]
                print("fetched ", len(retweets_list), " retweets")

                if retweets_list:
                    write_to_file(retweets_list, tid)
                    retweeter_names = []
                    retweeter_ids = []
                    retweeter_stats = {}
                    retweeter_stats.clear() #dict cleaning
                    retweeting_time = []
                    del retweeter_names[:] #initial cleaning
                    del retweeter_ids[:]
                    del retweeting_time[:]
                    for res in retweets_list:
                        tweeter_name = res['retweeted_status']['user']['screen_name']
                        tweeter_id = res['retweeted_status']['user']['id']
                        tweeter_folrs = res['retweeted_status']['user']['followers_count']
                        status_count = res['retweeted_status']['user']['statuses_count']
                        following = res['retweeted_status']['user']['friends_count']
                        tweet_time = res['retweeted_status']['created_at']
                        retweet_time = res['created_at']
                        retweet_time = to_datetime(retweet_time)
                        retweet_count = res['retweet_count']
                        rtwtr_name = res['user']['screen_name']
                        retweeter_stats[rtwtr_name] = [res['user']['followers_count'], \
                                                       res['user']['statuses_count'], \
                                                       res['user']['friends_count']]
                        rtwtr_id = res['user']['id']
                        retweeter_names.append(rtwtr_name)
                        retweeter_ids.append(rtwtr_id)
                        retweeting_time.append(retweet_time)
                    print("Original tweeter username: ", tweeter_name, "\n")

                    # format tweet time
                    tweet_time = to_datetime(tweet_time)

                    # fetch followers of original tweeter
                    folr_ids, fcal = gfn.get_followers_ids(tweeter_name, follower_calls)
                    follower_calls += fcal
                    print("current value of follower_calls: ", follower_calls)
                    print("Fetched {} (followers') twitter ids ..".format(len(folr_ids)))

                    # compute direct hop
                    L1_overlap, subset_check, disjoint_check = compute_hop1_overlap(retweeter_ids, folr_ids, tweeter_name)
                    print("subset, disjoint: ", subset_check, disjoint_check)

                    if subset_check:
                        tweeter_Vals = [1, tweeter_name, tweet_time, len(retweeter_names), 'Yes', 'No', tweeter_folrs, status_count, following]
                        retweeter_Vals = [retweeter_names, retweeting_time, "-", 'No', L1_overlap, retweeter_stats]

                        ptabled = prettyPrint(tweeter_Vals, retweeter_Vals)
                        output_stats(ptabled)

                        if total_calls_count < 15 and follower_calls < 15:
                            continue
                        else:
                            sleeper(900)
                            follower_calls = 0
                            total_calls_count = 0

                    else:
                        print("Not all retweeters are direct followers of original tweeter.")
                        not_dir_folrs_stats = make_friends_call(retweeter_ids, retweeter_names, folr_ids,
                                                          tweeter_name, tweeter_id, total_calls_count, friends_calls)
                        print("NOT-DIR-FOLRS-STATS:\n", not_dir_folrs_stats)

                        tweeter_Vals = [1, tweeter_name, tweet_time, len(retweeter_names), 'Yes', 'No', tweeter_folrs, status_count, following]
                        retweeter_Vals = [retweeter_names, retweeting_time, "-", 'No', L1_overlap, retweeter_stats]

                        ptabled = prettyTabled(tweeter_Vals, retweeter_Vals, not_dir_folrs_stats)
                        output_stats(ptabled)

                        if total_calls_count < 15 and follower_calls < 15:
                            continue
                        else:
                            sleeper(900)
                            follower_calls = 0
                            total_calls_count = 0

        else:
            continue


def make_friends_call(retweeter_ids, retweeter_names, folr_ids, tweeter_name, tweeter_id, calls_cnt, frnd_calls):
    """
    To find ids which are not direct followers of original tweeter.

    Get 'following/friends' persons ids.
    """
    not_direct_folrs = set(retweeter_ids).difference(set(folr_ids))
    direct_folrs = set(retweeter_ids).difference(not_direct_folrs)
    print("(DF + NDF) LEN: ", len(direct_folrs), "+", len(not_direct_folrs))

    rev_rtr_ids = list(reversed(retweeter_ids))
    rev_rtr_names = list(reversed(retweeter_names))

    idx_in_rtrs = []
    for elem in not_direct_folrs:
        idx_in_rtrs.append(rev_rtr_ids.index(elem))

    idx_in_rtrs.sort()
    to_call_tup = [(idx, rev_rtr_ids[idx], rev_rtr_names[idx]) for idx in idx_in_rtrs]
    print("REV RTR NM: ", rev_rtr_names, "--\n")
    print("REV RTR ID: ", rev_rtr_ids, "--\n")
    print("Not DirFol: ", not_direct_folrs, "--\n")
    print("To call ID: ", to_call_tup, "\n")

    to_call_ids = [(idx, ids) for idx, ids, name in to_call_tup]

    is_following_prev = {}
    frnd_call_res = []
    frnd_ids = []
    del frnd_ids[:]    #cleaning it

    frnd_call_cnt = frnd_calls
    for idx, _id in to_call_ids:
        if idx == 0:
            frnd_call_res.append((idx, _id, []))
        else:
            frnd_ids, frnd_call_cnt = gfi.get_friends_ids(rev_rtr_names[idx], calls_cnt)
            # to handle errors like: {'code': 34, 'message': 'Sorry, that page does not exist.'}
            # to handle 0 following cases(frnd_ids is empty result)
            if frnd_ids:
                frnd_call_res.append((idx, _id, frnd_ids))
            else:
                frnd_call_res.append((idx, _id, []))

        # to avoid RateLimitExceeded Error
        if frnd_call_cnt < 15 and calls_cnt < 15:
            calls_cnt += frnd_call_cnt
            print(" current value of total_calls: ", calls_cnt)
            sleeper(10)
        else:
            sleeper(960)
            frnd_call_cnt = 0
            calls_cnt = 0

    for idx, _id, ids in frnd_call_res:
        print("idx: ", idx, "-", _id, "--", len(ids))
        if idx == 0:
            intersect_res = find_intersection([tweeter_id], [], [tweeter_name])
        else:
            intersect_res = find_intersection(rev_rtr_ids[0:idx], ids, rev_rtr_names[0:idx])

        is_following = [tupl[0] for tupl in intersect_res]

        if sum(is_following):
            print(idx, "-", _id, "--", rev_rtr_names[idx], " is following ", rev_rtr_names[0:idx])
            print("is_following status:: ", intersect_res)
            is_following_prev[rev_rtr_names[idx]] = intersect_res
        else:
            if idx == 0:
                print(idx, "-", _id, "--", rev_rtr_names[idx], " is NOT following ", tweeter_name)
                print("is_following status:: ", intersect_res)
            else:
                print(idx, "-", _id, "--", rev_rtr_names[idx], " is NOT following ", rev_rtr_names[0:idx])
                print("is_following status:: ", intersect_res)

            is_following_prev[rev_rtr_names[idx]] = intersect_res

    return is_following_prev


def find_intersection(rtrIDs, frnd_ids, rtr_names):
    """To find whether a set is a subset of the  other."""
    print("comparing: RTR-IDS: ", rtrIDs, "--VS--", " FRND-IDS-LEN: ", len(frnd_ids))
    # will not work, if the user is not following all of the prev retweeters
    # is_subset = set(rtrIDs).issubset(set(frnd_ids))

    following_status = [(True, rtID, rtr_names[idx]) if rtID in frnd_ids else (False, rtID, rtr_names[idx]) for idx, rtID in enumerate(rtrIDs)]
    return following_status


def write_to_file(retweets, tid):
    """To write retweets to file."""
    fname = "../data/retweets/" + str(tid) + ".txt"
    with open(fname, 'w') as rwtfile:
        for rwt in retweets:
            rwtfile.write(str(rwt) + "\n")
    print("successfully written retweets to file: ", fname)


def compute_hop1_overlap(rtrIDS, folrIDS, twtr_name):
    """To determine overlap between user ANON's followers and
       retweeters of a particular tweet by user ANON
    """
    direct_folrs = []
    for ID in rtrIDS:
        if ID in folrIDS:
            direct_folrs.append(1)
        else:
            direct_folrs.append(0)

    # determine if (rtrIDS is subset of folrIDS)
    subset_chk = set(rtrIDS).issubset(set(folrIDS))
    disjoint_chk = set(rtrIDS).isdisjoint(set(folrIDS))

    return direct_folrs, subset_chk, disjoint_chk


def prettyPrint(twt_Vals, rwt_Vals):
    """To pretty print output using PrettyTable.
    This is for ALL-RETWEETERS are DIRECT FOLLOWERS of Original Tweeter case.
    """
    print("From prettyPrint function...\n")
    field_names = ["S.No", "UserID", "Re/TweetTime", "Retweets", "Orig.Tweet?", "Dir.Followr?", "#Followr", "#Tweets", "#Following"]
    tab = PrettyTable(field_names)
    tab.padding_width = 1
    tab.add_row(twt_Vals)

    # reverse the list for time: old->recent
    retweeters = list(reversed(rwt_Vals[0]))
    retweet_times = list(reversed(rwt_Vals[1]))
    f1 = rwt_Vals[2:4]
    is_dir_folrs = list(reversed(rwt_Vals[4]))
    f2 = rwt_Vals[5]

    for idx, rtr in enumerate(retweeters):
        sno = idx+2
        tab.add_row([sno, rtr, retweet_times[idx], *f1, is_dir_folrs[idx], *f2[rtr][:]])
    print(tab, "\n")

    return tab


def prettyTabled(twt_Vals, rwt_Vals, not_dir_folrs_stats):
    """To pretty print output using PrettyTable.
    This is for NOT-ALL-RETWEETERS are DIRECT FOLLOWERS of Original Tweeter case.
    """
    print("From prettyTabled function...\n")
    field_names = ["S.No", "UserID", "Re/TweetTime", "Retweets", "Orig.Tweet?", "Dir.Followr?", "#Followr", "#Tweets", "#Following"]
    tab = PrettyTable(field_names)
    tab.padding_width = 1
    tab.add_row(twt_Vals)

    # reverse the list for time: old->recent
    retweeters = list(reversed(rwt_Vals[0]))
    retweet_times = list(reversed(rwt_Vals[1]))
    f1 = rwt_Vals[2:4]
    is_dir_folrs = list(reversed(rwt_Vals[4]))
    f2 = rwt_Vals[5]

    ndfs = not_dir_folrs_stats
    for idx, booVal in enumerate(is_dir_folrs):
        rtr_name = retweeters[idx]
        if not booVal and rtr_name in ndfs:
            stats_tupl = ndfs[rtr_name]    #[(False, 26736333, 'anna'), (True, 9284112, 'brian')]
            for item in reversed(stats_tupl):
                if item[0]:
                    #refID is from the tweet arose
                    try:
                        refID = retweeters.index(item[2])
                        refID += 2  #since retweeters list starts @ 2 position in prettyprint table
                        is_dir_folrs[idx] = (refID, item[2])
                    except ValueError:
                        is_dir_folrs[idx] = (1, item[2]) #ref original tweeter; as in only 1 retweet case
                    #once found go to next ndf-retweeter
                    break
                else:
                    is_dir_folrs[idx] = (0, 'Unknown')
        else:
            continue


    for idx, rtr in enumerate(retweeters):
        sno = idx+2    #since retweeters list starts @ 2 position in prettyprint table
        tab.add_row([sno, rtr, retweet_times[idx], *f1, is_dir_folrs[idx], *f2[rtr][:]])
    print(tab, "\n")

    return tab



def output_stats(ptable):
    """To write PrettyTable output to file."""
    fname = "../data/result_stats/hop_statistics.txt"
    with open(fname, 'a') as af:
        af.write(str(ptable) + "\n\n\n")


if __name__ == '__main__':
    # parse command line arguments & get output filename
    parser = argparse.ArgumentParser()
    requiredArgs = parser.add_argument_group('must need arguments')
    requiredArgs.add_argument('-q', '--query', help='Query to be searched', required=True)
    requiredArgs.add_argument('-cnt', '--tweet_count', help='#tweets to be returned', required=True)
    requiredArgs.add_argument('-thresh', '--threshold', help='limits # followers of tweeter', required=True)
    requiredArgs.add_argument('-from', '--from_date', help='YYYY-MM-DD; from-date', required=True)
    requiredArgs.add_argument('-to', '--to_date', help='YYYY-MM-DD; to-date', required=True)
    requiredArgs.add_argument('-o', '--output_file', help='file for returned tweets', required=True)
    args = parser.parse_args()

    FILEPATH1 = os.getcwd() + os.path.sep + args.output_file
    if os.path.exists(FILEPATH1):
        sys.exit("output/retweets file already exists; Give new filename!")
    else:
        # creates an empty file
        open(args.output_file, 'a').close()

    auth = tweepy.auth.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    # keyphrase to search, from & to-date in which tweets need to be returned
    QUERY = args.query
    MAX_TWEETS = int(args.tweet_count)
    FOL_THRESH = int(args.threshold)
    FROM_DATE = args.from_date
    TO_DATE = args.to_date

    fetched_tweets = search_tweets_from_twitter_home(QUERY, MAX_TWEETS, FROM_DATE, TO_DATE)

    # write searched results(tweets) to output file
    with open(args.output_file, 'a') as ofile:
        for tw in fetched_tweets:
            ofile.write(str(tw) + "\n")
    print("successfully written the results to file: ", args.output_file)

    # offline processing of tweets starts from this point
    search_results_file = args.output_file
    twt_ids_set = extract_user_details(search_results_file)

    # get only tweet_ids
    extract_tid = lambda x: x[1]
    retweeted_tweet_ids = map(extract_tid, twt_ids_set)
    tweet_ids = list(retweeted_tweet_ids)
    print("extracted, ", len(tweet_ids), " ids from search results(tweets with atleast 1 retweet)")

    # reject tweeters with huge followers
    tweeter_tweetID_map = {item[1]: [item[0], item[2]] for item in twt_ids_set}

    # get retweets now
    print("\ngetting retweets of tweets now... ")
    get_retweets_for_tweetids(tweet_ids, tweeter_tweetID_map, FOL_THRESH)

