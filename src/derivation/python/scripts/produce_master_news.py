import pandas as pd
def main():

    factiva_df = pd.read_csv("../../../collection/python/output/news_articles.csv")
    wsj_df = factiva_df[factiva_df['source'].str.contains("Wall Street Journal")]
    wsj_df['source'] = "The Wall Street Journal"
    wsj_df['meeting_date'] = pd.to_datetime(wsj_df['meeting_date'])


    ft_df = pd.read_csv("../../../collection/python/output/ft_articles.csv")
    ft_df['source'] = "The Financial Times"
    ft_df['meeting_date'] = pd.to_datetime(ft_df['meeting_date'])

    nytimes_df = pd.read_csv("../../../collection/python/output/nytimes_articles.csv")
    nytimes_df['meeting_date'] = pd.to_datetime(nytimes_df['meeting_date'])
    nytimes_df['source'] = "The New York Times"
    nytimes_df.drop(columns=["link"],inplace=True)

    master_news = pd.concat([wsj_df,nytimes_df,ft_df],ignore_index=True)
    print(master_news)
    master_news.to_csv('../output/all_news_articles.csv')

main()