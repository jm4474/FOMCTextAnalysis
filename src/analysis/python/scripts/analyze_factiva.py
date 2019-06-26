import pandas as pd
import pprint
output_dir = "../../../collection/python/output/"
def main():
    derived_df = pd.read_csv("../../../collection/python/output/derived_data.csv")
    derived_df['end_date'] = pd.to_datetime(derived_df['end_date'])
    derived_df = derived_df[derived_df.event_type == "Meeting"]
    date_period = derived_df[(derived_df.end_date.dt.year >= 1988) & (derived_df.end_date.dt.year <= 2009)]
    meeting_dates = date_period[['end_date']]
    meeting_dates = meeting_dates.drop_duplicates(subset="end_date")
    meeting_dates['meeting_date'] = pd.to_datetime(meeting_dates['end_date'])
    meeting_dates = meeting_dates[['meeting_date']]

    news_df = pd.read_csv(output_dir+"news_articles.csv")

    total_articles = len(news_df)
    print("Total number of articles:{}".format(total_articles))
    content_df = news_df[news_df['content']!=""]
    print("Total number of articles with content:{}".format(len(content_df)))
    sources = {
        'nyt' : content_df[content_df['source'] == "The New York Times"],
        'wsj' : content_df[content_df['source'] == "The Wall Street Journal"],
        'ft' : content_df[content_df['source'] == "The Financial Times"]
    }


    for source in sources.keys():
        print("Total Number of Articles From {}:{}".format(source,sources[source]))
        unique_meetings = sources[source].drop_duplicates(subset="meeting_date")
        print("Total Number of meetings covered by {}:{}".format(source,len(unique_meetings)))
        print("Total Number of meetings missed by {}:{}".format(source,len(meeting_dates)-len(unique_meetings)))
main()