import pandas as pd
import pprint
import numpy as np
output_dir = "../../../derivation/python/output/"
from auxfunction_tablecreation import create_table_df
'''
@Author Anand Chitale
Produces summary statistics on the coverage of meetings by 
the financial times, nytimes, and wall street journal, 
reading in our master news data exporting to a latex file
'''
def main():
    comp_df = get_merge()
    print(comp_df)
    pivot = pd.pivot_table(comp_df,
                              values=['NYT', 'WSJ', 'FT'],
                              columns="year",
                              aggfunc=np.sum)

    pivot = pivot.reset_index()
    pivot.rename(columns={"index": "Newspaper"}, inplace=True)

    print(pivot)
    print(pivot.shape)
    create_table_df(pivot,"news_coverage")



def get_merge():
    derived_df = pd.read_csv("../../../collection/python/output/derived_data.csv")
    derived_df['end_date'] = pd.to_datetime(derived_df['end_date'])
    derived_df = derived_df[derived_df.event_type == "Meeting"]
    date_period = derived_df[(derived_df.end_date.dt.year >= 1988) & (derived_df.end_date.dt.year <= 2009)]
    meeting_dates = date_period[['end_date']]
    meeting_dates = meeting_dates.drop_duplicates(subset="end_date")
    meeting_dates['meeting_date'] = pd.to_datetime(meeting_dates['end_date'])
    meeting_dates = meeting_dates[['meeting_date']]

    news_df = pd.read_csv(output_dir+"all_news_articles.csv")

    total_articles = len(news_df)
    #print("Total number of articles:{}".format(total_articles))
    content_df = news_df[news_df['content']!=""]
    #print("Total number of articles with content:{}".format(len(content_df)))

    news_df['meeting_date'] = pd.to_datetime(news_df['meeting_date'])
    #print(news_df)
    merged_df = meeting_dates.merge(news_df,how="left",indicator=True,on="meeting_date")
    #print(merged_df)


    interm_df = pd.pivot_table(data=merged_df,index="meeting_date",columns="source",
                               values="headline",aggfunc=np.count_nonzero)

    interm_df = interm_df.reset_index()
    interm_df['year'] = interm_df.meeting_date.apply(lambda x: x.year)
    interm_df['NYT'] = interm_df["The New York Times"].notnull()
    interm_df['WSJ'] = interm_df["The Wall Street Journal"].notnull()
    interm_df['FT'] = interm_df["The Financial Times"].notnull()

    return interm_df




main()