import matplotlib.pyplot as plt
import streamlit as st
from scraper import TwitterScraper
from datetime import datetime, timedelta


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def v_spacer(height) -> None:
    for _ in range(height):
        st.write('\n')


def main():
    scraper = TwitterScraper()
    local_css("style.css")

    st.title('Twitter Smart Investing')

    search_placeholder = st.empty()
    search_keywords = search_placeholder.text_input('', placeholder='Search a Stock by Keyword')

    now = datetime.now()
    start_delta = timedelta(weeks=1)

    dates_placeholder = st.empty()
    empty_left, contents_left, contents_right, empty_right = dates_placeholder.columns([1, 1.5, 1.5, 1])
    start_date = contents_left.date_input("From", now - start_delta, max_value=datetime.now())
    end_date = contents_right.date_input("To", now, min_value=start_date, max_value=datetime.now())

    if search_keywords:
        v_spacer(height=2)

        graph_placeholder = st.empty()
        tweets_placeholder = st.empty()
        error_placeholder = st.empty()
        with st.spinner('Loading...'):
            # load the data
            scraper.fetch_data(search_keywords, start_date, end_date)
            # pass stock symbol, start date & end date
            buy, sell, hold = scraper.keywords_counter()
            investment_counts = [buy, sell, hold]
            max_value = max(investment_counts)
            best_option_index = list(investment_counts).index(max_value)

            # Pie chart
            fig, ax = plt.subplots(figsize=(8, 6))
            labels = ['Buy', 'Sell', 'Hold']
            colors = ['#2EFF2E', '#FF5C5C', '#C5C5C5']
            explode = (0.025, 0.025, 0.025)

            if sum(investment_counts) != 0:
                wedges, texts, autotexts = ax.pie(investment_counts, colors=colors,
                                                  autopct=lambda p: '{:.1f}%'.format(round(p)) if p > 0 else '',
                                                  startangle=90, pctdistance=0.85, explode=explode)

                for autotext in autotexts:
                    autotext.set_weight('bold')

                # Draw circle
                centre_circle = plt.Circle((0, 0), 0.75, fc='white')
                fig = plt.gcf()
                fig.gca().add_artist(centre_circle)
                ax.annotate(sum(investment_counts), xy=(0, 0), fontsize=50, weight='bold', ha="center")
                ax.annotate("Reviews", xy=(0, -0.25), fontsize=25, ha="center")

                # Draw bottom legend
                labels_counts = [str(count) + " " + label for count, label in zip(list(investment_counts), labels)]
                ax.legend(wedges, labels_counts, loc="lower center", ncol=3,
                          prop={'weight': 'bold'}, bbox_to_anchor=(0, -0.075, 1, 1))

                ax.axis('equal')
                ax.set_title(labels[best_option_index], y=1, weight='bold', fontsize=40, color=colors[best_option_index])

                graph_placeholder.pyplot(fig)

                v_spacer(height=1)

                # get best tweets
                tweets_df = scraper.get_popular_tweets().reset_index(drop=True)
                tweets_df.columns = ['User Name', 'Number of Followers', 'Tweet']
                tweets_placeholder.table(tweets_df)
            else:
                error_msg = '<p style="color:Red; font-size: 30px; text-align: center">No data found</p>'
                error_placeholder.markdown(error_msg, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
