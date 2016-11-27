import time
#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from httplib import IncompleteRead


#Variables that contains the user credentials to access Twitter API 
access_token = "fill-in token here"
access_token_secret = "fill-in access_token_secret here"
consumer_key = "fill-in consumer_key here"
consumer_secret = "fill-in consumer_secret here"

class StdOutListener(StreamListener):
    '''A basic listener that just prints received tweets(json response) to stdout.'''

    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status


if __name__ == '__main__':
    #handles Twitter authentication and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    #list the keywords that you want to fetch tweets about
    keyword_list = ['Saarland University', 'Computer Science', 'Cancer', 'Paris']

    while True:
        try:
            stream = Stream(auth, l)
            stream.filter(track=keyword_list, stall_warnings=True)

        except IncompleteRead as e:
            # Oh well, sleep sometime & reconnect and keep trying again & again
            time.sleep(15)
            continue

        except KeyboardInterrupt:
            stream.disconnect()
            break
