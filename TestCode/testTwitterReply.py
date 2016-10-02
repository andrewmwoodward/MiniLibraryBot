from twython import Twython, TwythonError
import time

#twitter credentials
apiKey = 'xxxxxxx'
apiSecret = 'xxxxxxxx'
accessToken = 'xxxxxxxxxx'
accessTokenSecret = 'xxxxxxxxxx'
api = Twython(apiKey, apiSecret, accessToken, accessTokenSecret)

a = 10
search_results = api.search(q="#MiniLibBot", count=1)

try:
    lastUser = ""
    while True:
        for tweet in search_results["statuses"]:
            if(lastUser == tweet["user"]["screen_name"]):
                print "already replied to this user"
            else:
                tweetStr = "@" +tweet["user"]["screen_name"]+ " There are " + str(a) + " books remaining in the mini library!"
                api.update_status(status = tweetStr, in_reply_to_status_id = tweet["id_str"])
                lastUser = tweet["user"]["screen_name"]
                print lastUser
        time.sleep(30)
except KeyboardInterrupt:
    print "Ending"
