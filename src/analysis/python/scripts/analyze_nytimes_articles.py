import pandas as pd
import numpy as np

def main():
    nyt_df = pd.read_csv("../../../collection/python/output/nytimes_articles.csv")

    number_articles = len(nyt_df)
    print("We currently have {} articles".format(number_articles))
    valid_articles = nyt_df[nyt_df['content']!=""]
    print("Out of those, we have {} valid articles".format(len(valid_articles)))
    #print(nyt_df.sort_values(by="article_date"))

    nyt_dates = valid_articles[['meeting_date']]
    nyt_dates['meeting_date'] = pd.to_datetime(nyt_dates['meeting_date'])
    nyt_dates = nyt_dates.drop_duplicates(subset="meeting_date")

    derived_df = pd.read_csv("../../../collection/python/output/derived_data.csv")
    derived_df['end_date'] = pd.to_datetime(derived_df['end_date'])
    derived_df = derived_df[derived_df.event_type=="Meeting"]
    date_period = derived_df[(derived_df.end_date.dt.year>=1988)&(derived_df.end_date.dt.year<=2009)]

    meeting_dates = date_period[['end_date']]

    meeting_dates = meeting_dates.drop_duplicates(subset="end_date")
    meeting_dates['meeting_date'] = pd.to_datetime(meeting_dates['end_date'])
    meeting_dates = meeting_dates[['meeting_date']]

    merged = meeting_dates.merge(nyt_dates,how="outer",indicator=True)
    diff = merged[merged._merge!="both"]
    print("Out of all {} meetings, we have articles for {}".format(len(meeting_dates),len(nyt_dates)))
    print("There are {} Meetings without articles".format(len(diff)))


    comp_df = pd.DataFrame(merged)
    comp_df['d_meeting'] = True
    comp_df['d_nyt'] = comp_df['_merge']=="both"
    comp_df['year'] = comp_df['meeting_date'].dt.year
    comp_df = comp_df[['d_meeting','d_nyt','year','meeting_date']]
    print(comp_df)

    pivot_df = pd.pivot_table(comp_df,
                              values=['d_meeting','d_nyt'],
                              columns="year",
                              aggfunc= np.sum
                              )
    print(pivot_df)
    print(pivot_df.shape)
main()