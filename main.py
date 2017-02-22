import json

from twitter import trends

from nltk.sentiment.vader import SentimentIntensityAnalyzer

from pymongo import MongoClient

mongo = MongoClient("db", 27017)
db = mongo.database


def clear_database():
    db.tweets.remove({})
    db.topics.remove({})
    db.analysis.remove({})


def initialise_topics():
    topics = [{
        "name": "Trump",
        "queries": ["trump", "@realDonaldTrump", "@POTUS"]
    }, {
        "name": "Grammys",
        "queries": ["#GRAMMYs", "#grammys2017"]
    },{
        "name":"NMEAwards",
        "queries":["#NMEAwards","@nme"]
    },{
        "name":"PS4",
        "queries":["#ps4","#ps4pro","@Playstation","@PlayStationUK"]
    },{
        "name":"XBox",
        "queries":["Xbox one","Xbox 360","@Xbox","#xbox"]
    },{
        "name":"Machine Learning",
        "queries":["#ArtificialIntelligence","#machinelearning","#deeplearning","@DeepMindAI"]
    },{
        "name":"UEFA",
       "queries":["UEFA","#ChampionsLeague","@Arsenal","@realmadriden","ParisSaintGermain","#Barcelona","#FCBARS","#UCL"]
    },{
        "name":"Fashion Week",
        "queries":["@TwitterFashion","#FashionWeek","New York Fashion Week","London Fashion Week","Milan Fashion Week","Paris Fashion Week"]
    },{
        "name":"Hospital", 
        "queries":["#hospital","#nhs","@bbctwo"]
    },{
        "name":"French Presidential election",
        "queries":["French President election","Le Pen","#Hollande"]
    },{
        "name":"Cute Cats",
        "queries":["#CatsOfTwitter","@Cats","#cute","#cats","#catlovers"]
    },{
        "name":"Beauty and the Beast", 
        "queries":["#beautyandthebeast","#BeautyAndTheBeast","#beourguest","@beourguest","@thereallukevans","@emmawatson","#lukeevans"]
    },{
        "name":"Super Bowl",
        "queries":["#SuperBowl","@SuperBowl","#SB51","#patriots"]
    }
]
    # retrieve trends in UK woeid
    #trends = twitter.trends.place(_id = 23424975)
    #for location in trends:
    #    for trend in location["trends"]:
    #        
    topics_result = dict()
    for t in topics:
        res = db.topics.insert_one(t)
        topics_result[res.inserted_id] = t
    return topics_result


def read_tweets(filename):
    tweets = []
    with open(filename, "r") as f:
        for r in f.readlines():
            if len(r.strip()) == 0:
                continue
            tweets.append(json.loads(r))
    return tweets


def get_topic_id(tweet, topics):
    # TODO: determine correct topic (this should be known when the data is queried,
    # so ideally we would just retrieve this data from the JSON file)
    return list(topics.keys())[0]


def get_sentiment(tweet):
    sid = SentimentIntensityAnalyser()
    ss = sid.polarity_scores()
    compund = ss['compound']
    return compund

def get_location_data(tweet):
    return tweet['coordinates'] if 'coordinates' in tweet else None


def process_tweet(tweet, topics):
    topic = get_topic_id(tweet, topics)
    sentiment = get_sentiment(tweet)
    location = get_location_data(tweet)
    return {
        "topic": topic,
        "sentiment": sentiment,
        "text": tweet['text'] if 'text' in tweet else "NO TEXT",
        "location": location
    }


def store_processed_tweet(tweet):
    res = db.processed_tweets.insert_one(tweet)
    return res.inserted_id


def store_topic(topic_id, region_id, analysis):
    # TODO: add interval
    res = db.analysis.insert_one({
        "topic_id": topic_id,
        "region_id": region_id,
        "analysis": analysis
    })
    print("Stored data for topic {} in region {}. Analysis = {}".format(
        topic_id, region_id, analysis))
    return res.inserted_id


def get_all_regions():
    return [{
        "_id": "<SHOULD BE IN MONGO>{}".format(i),
        "name": "REGION{}".format(i)
    } for i in range(10, 20)]

def get_all_tweet_regions(tweet):
    return ["<SHOULD BE IN MONGO>13"]


def process_topic(topic_id):
    # TODO: add interval
    topic_tweets = db.processed_tweets.find({"topic": topic_id})
    regions = {region["_id"]: [] for region in get_all_regions()}
    for tweet in topic_tweets:
        tweet_regions = get_all_tweet_regions(tweet)
        for region in tweet_regions:
            regions[region].append(tweet)
    for region_id in regions:
        tweets = regions[region_id]
        if len(tweets) == 0:
            average_sentiment = 0
        else:
            average_sentiment = sum([t['sentiment']['avg'] for t in tweets]) / len(tweets)
        analysis_id = store_topic(topic_id, region_id, {
            "average_sentiment": average_sentiment
        })


def main():
    clear_database()
    topics_data = initialise_topics()

    all_tweets = read_tweets("tweet_9_2_2017.json")
    processed_tweet_ids = set()
    for t in all_tweets:
        processed_tweet = process_tweet(t, topics_data)
        if processed_tweet is not None:
            processed_tweet_ids.add(store_processed_tweet(processed_tweet))

    for t in topics_data:
        process_topic(t)


if __name__ == "__main__":
    main()
