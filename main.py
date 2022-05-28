import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import scraper


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def v_spacer(height) -> None:
    for _ in range(height):
        st.write('\n')


def main():
    local_css("style.css")

    placeholder = st.title('Twitter Smart Investing')
    search = st.text_input('', placeholder='Search a Stock Symbol')

    if search:
        v_spacer(height=2)

        with st.spinner('Loading...'):
            # DUMMY DATA
            # investment_options = pd.Index([0, 0, 1, 1, 2, 2, 2])
            sell, buy, hold = scraper.keywords_counter()
            print(sell, buy, hold)

            # investment_counts = investment_options.value_counts()
            investment_counts = [sell, buy, hold]

            max_value = max(investment_counts)
            best_option_index = list(investment_counts).index(max_value)

            # Pie chart
            fig, ax = plt.subplots(figsize=(8, 6))
            labels = ['Buy', 'Sell', 'Hold']
            colors = ['#2EFF2E', '#FF5C5C', '#C5C5C5']
            explode = (0.025, 0.025, 0.025)
            wedges, texts, autotexts = ax.pie(investment_counts, colors=colors, autopct='%1.1f%%',
                                              startangle=90, pctdistance=0.85, explode=explode)
            for autotext in autotexts:
                autotext.set_weight('bold')

            # Draw circle
            centre_circle = plt.Circle((0, 0), 0.75, fc='white')
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)
            ax.annotate(sell + buy + hold, xy=(0, 0), fontsize=50, weight='bold', ha="center")
            ax.annotate("Reviews", xy=(0, -0.25), fontsize=25, ha="center")

            # Draw bottom legend
            labels_counts = [str(count) + " " + label for count, label in zip(list(investment_counts), labels)]
            ax.legend(wedges, labels_counts, loc="lower center", ncol=3,
                      prop={'weight': 'bold'}, bbox_to_anchor=(0, -0.075, 1, 1))

            ax.axis('equal')
            ax.set_title(labels[best_option_index], y=1, weight='bold', fontsize=40, color=colors[best_option_index])

            st.pyplot(fig)


if __name__ == '__main__':
    main()
