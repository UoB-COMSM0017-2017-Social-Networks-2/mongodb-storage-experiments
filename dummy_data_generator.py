import json
import math
import csv
import io

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
    THRESHOLD = .2

    def __init__(self, topic, location, sentiment, time):
        self.topic = topic
        self.time = time
        self.location = location
        self.sentiment = sentiment

    def positive_sentiment(self):
        return self.sentiment > Tweet.THRESHOLD

    def negative_sentiment(self):
        return self.sentiment < -Tweet.THRESHOLD

    def neutral_sentiment(self):
        return -Tweet.THRESHOLD <= self.sentiment <= Tweet.THRESHOLD


today = 1487548800
minute = 60
hour = 60 * minute


def get_location_data(woeids):
    result = dict()
    for w in woeids:
        d = woeids[w]
        result[w] = d
    return result


def get_intervals():
    start_time = today
    time_resolution = 6 * hour
    intervals = []
    for i in range(4):
        interval_start = i * time_resolution + start_time
        interval_end = interval_start + time_resolution
        intervals.append({
            "start": interval_start,
            "end": interval_end
        })
    return intervals


def get_topic_tweets(tweets, topic):
    return {tweet for tweet in tweets if tweet.topic == topic}


def get_tweets_in_interval(tweets, interval):
    return {tweet for tweet in tweets if interval["start"] <= tweet.time < interval["end"]}


def get_topic_time_data(topic_tweets):
    result = []
    for interval in get_intervals():
        interval_start = interval["start"]
        interval_end = interval["end"]
        interval_tweets = get_tweets_in_interval(topic_tweets, interval)
        average_sentiment = math.nan
        if len(interval_tweets) > 0:
            average_sentiment = sum(
                [tweet.sentiment for tweet in interval_tweets]) / float(len(interval_tweets))
        num_pos = sum(
            [1 for tweet in topic_tweets if tweet.positive_sentiment()])
        num_neg = sum(
            [1 for tweet in topic_tweets if tweet.negative_sentiment()])
        num_neut = sum(
            [1 for tweet in topic_tweets if tweet.neutral_sentiment()])
        result.append({
            "interval_start": interval_start,
            "interval_end": interval_end,
            "popularity": len(interval_tweets),
            "average_sentiment": average_sentiment,
            "sentiment_distribution": {
                "positive": num_pos,
                "negative": num_neg,
                "neutral": num_neut
            }
        })

    return result


def get_location_topic_data(tweets):
    average_sentiment = math.nan
    if len(tweets) > 0:
        average_sentiment = sum(
            [tweet.sentiment for tweet in tweets]) / float(len(tweets))
    return {
        "popularity": len(tweets),
        "sentiment": average_sentiment
    }


def write_stream_chart_data(tweets, filename):
    with open('output/{}.csv'.format(filename), 'w') as csv_file:
        csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
        pos_lines = []
        neut_lines = []
        neg_lines = []
        # group per time interval
        data = get_topic_time_data(tweets)
        for interval in data:
            timestamp = (interval["interval_start"] +
                         interval["interval_end"]) // 2
            pos_lines.append(
                ["POS", interval["sentiment_distribution"]["positive"], timestamp])
            neut_lines.append(
                ["NEUT", interval["sentiment_distribution"]["neutral"], timestamp])
            neg_lines.append(
                ["NEG", interval["sentiment_distribution"]["negative"], timestamp])

        for line in pos_lines + neut_lines + neg_lines:
            csv_writer.writerow(line)


def get_positive_ratio(tweets):
    nb_pos = sum([1 for tweet in tweets if tweet.sentiment >= 0])
    nb_neg = sum([1 for tweet in tweets if tweet.sentiment < 0])
    return nb_pos / (nb_pos + nb_neg)


def get_overall_sentiment(tweets):
    nb_pos = sum([1 for tweet in tweets if tweet.positive_sentiment()])
    nb_neg = sum([1 for tweet in tweets if tweet.negative_sentiment()])
    nb_neut = sum([1 for tweet in tweets if tweet.neutral_sentiment()])
    if nb_pos > max(nb_neg, nb_neut):
        return 1
    if nb_neg > max(nb_pos, nb_neut):
        return -1
    return 0


def write_bubble_chart_data(tweets, filename):
    with open('output/{}.csv'.format(filename), 'w') as csv_file:
        csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        topics = {tweet.topic for tweet in tweets}
        for topic in topics:
            topic_tweets = get_topic_tweets(tweets, topic)
            csv_writer.writerow([
                topic, topic, len(topic_tweets), get_overall_sentiment(
                    topic_tweets), get_positive_ratio(topic_tweets)
            ])


def main():
    all_tweets = [
        Tweet("Trump", "Scotland", -.5, today + 3 * hour + 2 * minute),
        Tweet("Trump", "Scotland", -.2, today + 2 * hour + 1 * minute),
        Tweet("Trump", "United Kingdom", .8, today + 5 * hour + 15 * minute),
        Tweet("Trump", "Bath", .2, today + 5 * hour + 13 * minute),
        Tweet("Trump", "Bristol", -.7, today + 3 * hour + 53 * minute),
        Tweet("Trump", "Bath", .3, today + 13 * hour + 9 * minute),
        Tweet("Trump", "Bath", -1, today),
        Tweet("Trump", "Cardiff", -.8, today + 9 * hour),
        Tweet("Valentine", "London", .5, today + 6 * hour + 2 * minute),
        Tweet("Valentine", "London", -.7, today + 1 * hour + 1 * minute),
        Tweet("Valentine", "United Kingdom", .9,
              today + 19 * hour + 15 * minute),
        Tweet("Valentine", "Cardiff", -.1, today + 5 * hour + 23 * minute),
        Tweet("Valentine", "Bristol", -.5, today + 3 * hour + 53 * minute),
        Tweet("Valentine", "Bristol", .2, today + 19 * hour + 9 * minute),
        Tweet("Valentine", "Bath", 1, today),
        Tweet("Valentine", "Cardiff", -.8, today + 9 * hour)
    ]
    result = dict()
    result["locations"] = get_location_data(woeids)
    result["data"] = list()
    topics = {t.topic for t in all_tweets}

    # Bubble chart data
    for interval in get_intervals():
        write_bubble_chart_data(
            get_tweets_in_interval(all_tweets, interval),
            "bubble_chart_interval_{}".format(interval["start"])
        )

    for topic in topics:
        topic_tweets = [tweet for tweet in all_tweets if tweet.topic == topic]

        # Stream chart data
        write_stream_chart_data(
            topic_tweets, "stream_chart_topic_{}".format(topic))
        for woeid in woeids:
            location_topic_tweets = {
                tweet for tweet in topic_tweets if is_in_region(tweet.location, woeid)}
            write_stream_chart_data(
                location_topic_tweets, "stream_chart_topic_{}_location_{}".format(topic, woeid))

        result["data"].append({
            "topic": topic,
            "times": get_topic_time_data(topic_tweets),
            "locations": {
                woeids[woeid]: get_location_topic_data(
                    {tweet for tweet in topic_tweets if is_in_region(
                        tweet.location, woeid)}
                ) for woeid in woeids
            }
        })
    output = io.StringIO()
    csv_data = ["A", 1, 2, "test"]
    csv_writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    csv_writer.writerow(csv_data)
    print(output.getvalue())
    print(json.dumps(result))

if __name__ == "__main__":
    main()
