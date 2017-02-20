import json
import math

woeids = {
        "Scotland": 12578048,
        "Bristol": 13963,
        "London": 44418,
        "United Kingdom": 23424975,
        "England": 24554868,
        "Bath": 12056,
        "Cardiff": 15127,
        "Wales": 12578049
        }
location_parents = {
        "Scotland": "United Kingdom",
        "Bristol": "England",
        "England": "United Kingdom",
        "London": "England",
        "Bath": "England",
        "Cardiff": "Wales",
        "Wales": "United Kingdom"
        }

def is_in_region(location, region):
    if location == region:
        return True
    if location in location_parents:
        return is_in_region(location_parents[location], region)
    return False

class Tweet:
    def __init__(self, topic, location, sentiment, time):
        self.topic = topic
        self.time = time
        self.location = location
        self.sentiment = sentiment


today = 1487548800
minute = 60
hour = 60*minute

def get_location_data(woeids):
    result = dict()
    for w in woeids:
        d = woeids[w]
        result[w] = d
    return result

def get_topic_time_data(topic_tweets):
    start_time = today
    time_resolution = 6*hour
    result = []
    for i in range(4):
        interval_start = i * time_resolution + start_time
        interval_end = interval_start + time_resolution
        interval_tweets = {tweet for tweet in topic_tweets if interval_start <= tweet.time < interval_end}
        average_sentiment = math.nan 
        if len(interval_tweets) > 0:
            average_sentiment = sum([tweet.sentiment for tweet in interval_tweets]) / float(len(interval_tweets))
        result.append({
            "interval_start": interval_start,
            "interval_end": interval_end,
            "popularity": len(interval_tweets),
            "sentiment": average_sentiment
            })
    return result

def get_location_topic_data(tweets):
    average_sentiment = math.nan
    if len(tweets) > 0:
        average_sentiment = sum([tweet.sentiment for tweet in tweets]) / float(len(tweets))
    return {
            "popularity": len(tweets),
            "sentiment": average_sentiment
            }


def main():
    all_tweets = [
            Tweet("Trump", "Scotland", -.5, today + 3 * hour + 2 * minute),
            Tweet("Trump", "Scotland", -.2, today + 2 * hour + 1 * minute),
            Tweet("Trump", "United Kingdom", .8, today + 5 * hour + 15 * minute),
            Tweet("Trump", "Bath", .2, today + 5*hour + 13 * minute),
            Tweet("Trump", "Bristol", -.7, today + 3 * hour + 53 *  minute),
            Tweet("Trump", "Bath", .3, today + 13 * hour + 9 * minute),
            Tweet("Trump", "Bath", -1, today),
            Tweet("Trump", "Cardiff", -.8, today + 9 * hour),
            Tweet("Valentine", "London", .5, today + 6 * hour + 2 * minute),
            Tweet("Valentine", "London", -.7, today + 1 * hour + 1 * minute),
            Tweet("Valentine", "United Kingdom", .9, today + 19 * hour + 15 * minute),
            Tweet("Valentine", "Cardiff", -.1, today + 5*hour + 23 * minute),
            Tweet("Valentine", "Bristol", -.5, today + 3 * hour + 53 *  minute),
            Tweet("Valentine", "Bristol", .2, today + 19 * hour + 9 * minute),
            Tweet("Valentine", "Bath", 1, today),
            Tweet("Valentine", "Cardiff", -.8, today + 9 * hour)
            ]
    result = dict()
    result["locations"] = get_location_data(woeids)
    result["data"] = list()
    topics = {t.topic for t in all_tweets}
    for topic in topics:
        topic_tweets = [tweet for tweet in all_tweets if tweet.topic == topic]
        result["data"].append({
            "topic": topic,
            "times": get_topic_time_data(topic_tweets),
            "locations": {
                woeids[woeid] : get_location_topic_data(
                    {tweet for tweet in topic_tweets if is_in_region(tweet.location, woeid)}
                    ) for woeid in woeids
                }
            })
    print(json.dumps(result))

if __name__ == "__main__":
    main()
