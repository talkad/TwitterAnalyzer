from twython import Twython
import pandas as pd
from datetime import date, timedelta
from functools import reduce

pd.set_option('display.max_colwidth', 5000)

# credentials
credentials = {}
credentials['CONSUMER_KEY'] = 'jIqsiEj6Bp3B5nMNlVuGrlwXv'
credentials['CONSUMER_SECRET'] = 'xFXTXFFOpk3iCCm7wXlSyUpIjlmJSx1pZ4gq4pESK1839r0G8S'
credentials['ACCESS_TOKEN'] = '1516112252390330372-BU5TxsLR26Iv59Ue3qSrlzA0kds4Nb'
credentials['ACCESS_SECRET'] = 'FwF7fbNGDbqLG7l5NViQrSNkeUJelTnpW4S0hTGMS2QZ4'

python_tweets = Twython(credentials['CONSUMER_KEY'], credentials['CONSUMER_SECRET'], credentials['ACCESS_TOKEN'],
                        credentials['ACCESS_SECRET'])

since_date = '2022-04-10'
until_date = '2022-04-17'
tokens_required = ["AMZN"]  # ["AMZN", "amazon", "#amazon", "amzn", "@amazon"]
keywords = {
    'buy_words': ["outperform", "buy", "sector perform", "hot", "bulles", "overweight", "positive", "strong buy"],
    'sell_words': ["sell", "underperform", "underweight", "underwt", "in-line", "frozen", "bleeding", "reduce"],
    'holding_words': ["hold", "neutral", "market perform"]}


def fetch_data(startDate, endDate):
    COUNT_TWEETS__FETCHED = 500
    TWEETS_PER_REQUEST = 100
    MAX_ATTEMPTS = int((COUNT_TWEETS__FETCHED / TWEETS_PER_REQUEST) * 2)
    LANG = 'en'
    data = {'user': [], 'date': [], 'text': [], 'favorite_count': [], 'followers_count': []}

    # start_date = date(2022, 4, 10)
    # end_date = date(2022, 4, 16)
    start_date = startDate
    end_date = endDate

    delta = timedelta(days=7)
    for token in tokens_required:

        while start_date <= end_date:
            since = start_date.strftime("%Y-%m-%d")
            start_date += delta
            until = start_date.strftime("%Y-%m-%d")

            for i in range(MAX_ATTEMPTS):

                if COUNT_TWEETS__FETCHED <= len(data['user']):
                    print(f"You fetched {len(data['user'])} tweets at date {start_date}")
                    break

                query = {'q': token,
                         'count': TWEETS_PER_REQUEST,
                         'lang': LANG,
                         'since': since,
                         'until': until
                         }

                # Query Twitter
                if i == 0:
                    # Query twitter for data - no max_id
                    results = python_tweets.search(**query)
                else:
                    # Query twitter for data - with max_id
                    results = python_tweets.search(**query, max_id=next_max_id)

                print(f'result: {results}')

                # Save the returned tweets
                for status in results['statuses']:
                    data['user'].append(status['user']['screen_name'])
                    data['date'].append(status['created_at'])
                    data['text'].append(status['text'])
                    data['favorite_count'].append(status['favorite_count'])
                    data['followers_count'].append(status['user']['followers_count'])

                # Get the next max_id
                try:
                    next_results_url_params = results['search_metadata']['next_results']
                    next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
                except:
                    break

    return data


def occurences_counter(lst, tweet):
    return reduce(lambda acc, curr: acc + tweet.lower().split().count(curr), lst, 0)


def keywords_counter(start_date, until_date):
    df = fetch_data(start_date, until_date)
    df = pd.DataFrame(df)

    keywords['buy_words'] += list(map(lambda word: word + '!', keywords['buy_words'])) + list(
        map(lambda word: word + ',', keywords['buy_words'])) + list(map(lambda word: word + '.', keywords['buy_words']))
    keywords['sell_words'] += list(map(lambda word: word + '!', keywords['sell_words'])) + list(
        map(lambda word: word + ',', keywords['sell_words'])) + list(map(lambda word: word + '.', keywords['sell_words']))
    keywords['holding_words'] += list(map(lambda word: word + '!', keywords['holding_words'])) + list(
        map(lambda word: word + ',', keywords['holding_words'])) + list(map(lambda word: word + '.', keywords['holding_words']))

    sell_words = df.apply(lambda row: occurences_counter(keywords['sell_words'], row['text']), axis=1)
    buy_words = df.apply(lambda row: occurences_counter(keywords['buy_words'], row['text']), axis=1)
    hold_words = df.apply(lambda row: occurences_counter(keywords['hold_words'], row['text']), axis=1)

    return 5, 5, 10

    # return sell_words.sum(), buy_words.sum(), hold_words.sum()

