from twython import Twython
import pandas as pd
from datetime import timedelta, date
from functools import reduce
import random

pd.set_option('display.max_colwidth', 5000)


def occurences_counter(lst, tweet):
    return reduce(lambda acc, curr: acc + tweet.lower().split().count(curr), lst, 0)


class TwitterScraper:
    def __init__(self):
        self.credentials = {}
        self.update_creds()
        self.python_tweets = Twython(self.credentials['CONSUMER_KEY'], self.credentials['CONSUMER_SECRET'],
                                     self.credentials['ACCESS_TOKEN'], self.credentials['ACCESS_SECRET'])
        self.tokens_required = {"amazon": ["$amzn", "AMZN", "amazon", "#amazon", "amzn", "@amazon"],
                                "facebook": ["Facebook", "facebook", "meta", "fb", "#fb", "$fb"],
                                "tesla": ["Tsla", "tsla", "$tsla", "#tesla", "eilonmusk"],
                                "ford": ["Ford", "ford", "f", "#f", "$f"]
                                }
        self.keywords = {
            'buy_words': ["outperform", "buy", "sector perform", "hot", "bulles", "overweight", "positive",
                          "strong buy"],
            'sell_words': ["sell", "underperform", "underweight", "underwt", "in-line", "frozen", "bleeding", "reduce"],
            'holding_words': ["hold", "neutral", "market perform"]}
        self.add_keywords()

        self.df = pd.DataFrame({'user': [], 'followers_count': [], 'text': []})

    def update_creds(self):
        self.credentials['CONSUMER_KEY'] = 'ilrnqE4DksBSk7KfDBk2IF1xh'
        self.credentials['CONSUMER_SECRET'] = 's7L55GAL70VWLKZgf6ABGd4WozHUwGDmDD8BGwBWSZ03VJnOkY'
        self.credentials['ACCESS_TOKEN'] = '1516112252390330372-w4HYVMnK0lBKmSzcInJOPbJ70NQ0M7'
        self.credentials['ACCESS_SECRET'] = 'lwYUTdFppmBh3E1paIVpdg8fmiApo0HwCgSrMeGAOlV5c'

    def fetch_data(self, stock_name, startDate, endDate):
        # init
        self.df = pd.DataFrame({'user': [], 'followers_count': [], 'text': []})

        all_keywords = self.keywords['buy_words'] + self.keywords['sell_words'] + self.keywords['holding_words']

        COUNT_TWEETS__FETCHED = 1000  # TODO: change it to 2000
        total = 0
        itr_idx = 0
        TWEETS_PER_REQUEST = 100
        # MAX_ATTEMPTS = int((COUNT_TWEETS__FETCHED / TWEETS_PER_REQUEST) * 2)

        exceeding_max_amount = False
        LANG = 'en'
        data = {'user': [], 'date': [], 'text': [], 'favorite_count': [], 'followers_count': []}

        # check if stock name exists
        if stock_name not in self.tokens_required.keys():
            return data

        # shuffle tokens
        tokens = self.tokens_required[stock_name]
        random.shuffle(tokens)

        start_date = startDate
        end_date = endDate

        delta = timedelta(days=7)
        for token in tokens:

            if exceeding_max_amount:
                break

            while start_date <= end_date and not exceeding_max_amount:
                since = start_date.strftime("%Y-%m-%d")
                start_date += delta
                # until = start_date.strftime("%Y-%m-%d")

                week_bound = True
                first_itr = True

                # for i in range(MAX_ATTEMPTS):
                while week_bound:

                    itr_idx += 1

                    if COUNT_TWEETS__FETCHED <= total:
                        exceeding_max_amount = True
                        print(f"Fetched {total} tweets at date {since}")
                        break

                    query = {'q': token,
                             'count': TWEETS_PER_REQUEST,
                             'lang': LANG,
                             'since': since,
                             # 'until': until
                             }

                    # Query Twitter
                    if first_itr:
                        # Query twitter for data - no max_id
                        results = self.python_tweets.search(**query)
                    else:
                        # Query twitter for data - with max_id
                        results = self.python_tweets.search(**query, max_id=next_max_id)

                    first_itr = False

                    total += len(results['statuses'])

                    # Save the returned tweets
                    for status in results['statuses']:

                        # save only at least one keyword exists in tweet
                        if occurences_counter(all_keywords, status['text']) > 0:
                            # if any(term in status['text'] for term in all_keywords):

                            data['user'].append(status['user']['screen_name'])
                            data['date'].append(status['created_at'])
                            data['text'].append(status['text'])
                            data['favorite_count'].append(status['favorite_count'])
                            data['followers_count'].append(status['user']['followers_count'])

                    # print stats
                    print(f"({itr_idx}) found {len(data['user'])} out of {total} tweets loaded")

                    # Get the next max_id
                    try:
                        next_results_url_params = results['search_metadata']['next_results']
                        next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
                    except Exception as e:
                        week_bound = False

        self.df = pd.DataFrame(data)[['user', 'followers_count', 'text']]
        return data

    def add_keywords(self):
        self.keywords['buy_words'] += list(map(lambda word: word + '!', self.keywords['buy_words'])) + list(
            map(lambda word: word + ',', self.keywords['buy_words'])) + list(
            map(lambda word: word + '.', self.keywords['buy_words']))
        self.keywords['sell_words'] += list(map(lambda word: word + '!', self.keywords['sell_words'])) + list(
            map(lambda word: word + ',', self.keywords['sell_words'])) + list(
            map(lambda word: word + '.', self.keywords['sell_words']))
        self.keywords['holding_words'] += list(map(lambda word: word + '!', self.keywords['holding_words'])) + list(
            map(lambda word: word + ',', self.keywords['holding_words'])) + list(
            map(lambda word: word + '.', self.keywords['holding_words']))

    def keywords_counter(self):

        # check if dataframe is empty
        if self.df.empty:
            return 0, 0, 0

        sell_words = self.df.apply(lambda row: occurences_counter(self.keywords['sell_words'], row['text']), axis=1)
        buy_words = self.df.apply(lambda row: occurences_counter(self.keywords['buy_words'], row['text']), axis=1)
        hold_words = self.df.apply(lambda row: occurences_counter(self.keywords['holding_words'], row['text']), axis=1)

        return sell_words.sum(), buy_words.sum(), hold_words.sum()

    def get_popular_tweets(self):
        return self.df.sort_values(by='followers_count', ascending=False).head(10)[['user', 'followers_count', 'text']]


# scraper = TwitterScraper()
# d = scraper.fetch_data("tesla", date(2022, 4, 1), date(2022, 4, 20))
# print(scraper.keywords_counter())
