from nltk.sentiment.vader import SentimentIntensityAnalyzer

sid = SentimentIntensityAnalyzer()

class sentiment(object):

    def __init__(self, tweet_text):
        self.tweet_text = tweet_text

    def compound(self):
        if self.tweet_text is None:
            return None
        else:
            ss = sid.polarity_scores(self.tweet_text)
            comp = ss['pos']
            return comp

    def positive(self):
        if self.tweet_text is None:
            return None
        else:
            ss = sid.polarity_scores(self.tweet_text)
            pos = ss['pos']
            return pos

    def neutral(self):
        if self.tweet_text is None:
            return None
        else:
            ss = sid.polarity_scores(self.tweet_text)
            neut = ss['neu']
            return neut

    def negative(self):
        if self.tweet_text is None:
            return None
        else:
            ss = sid.polarity_scores(self.tweet_text)
            neg = ss['neg']
            return neg
