import pandas as pd
def main():
    nytimes_df = pd.read_csv("../../../collection/python/output/nytimes_articles.csv")
    factiva_df = pd.read_csv("../../../collection/python/output/news_articles.csv")
    factiva_wo_nyt_df = factiva_df[factiva_df.source!="The New York Times"]

    nytimes_df['meeting_date'] = pd.to_datetime(nytimes_df['meeting_date'])
    nytimes_df['source'] = "The New York Times"
    nytimes_df.drop(columns=["link"],inplace=True)
    factiva_wo_nyt_df['meeting_date'] = pd.to_datetime(factiva_wo_nyt_df['meeting_date'])

    #print(nytimes_df)
    #print(factiva_wo_nyt_df)
    master_news = pd.concat([factiva_wo_nyt_df,nytimes_df],ignore_index=True)
    print(master_news)
    master_news.to_csv('../output/all_news_articles.csv')

main()