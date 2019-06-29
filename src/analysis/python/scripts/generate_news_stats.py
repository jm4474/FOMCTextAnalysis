import pandas as pd
import pprint
import numpy as np
output_dir = "../../../derivation/python/output/"

def main():
    comp_df = get_merge()
    print(comp_df)
    pivot = pd.pivot_table(comp_df,
                              values=['NYT', 'WSJ'],
                              columns="year",
                              aggfunc=np.sum)

    pivot = pivot.reset_index()
    pivot.rename(columns={"index": "Newspaper"}, inplace=True)

    print(pivot)
    print(pivot.shape)
    create_table_df(pivot,"news_coverage")

def create_table_df(data, name):
    columnheaders = list(data.columns)
    numbercolumns = len(columnheaders)

    with open("../output/" + name + ".tex", "w") as f:
        f.write(r"\begin{tabular}{" + "l" + "".join("c" * (numbercolumns - 1)) + "}\n")
        f.write("\\hline\\hline \n")
        f.write("\\addlinespace" + " \n")
        f.write(" & ".join([str(x) for x in columnheaders]) + " \\\ \n")
        f.write("\\hline \n")
        # write data
        for idx, row in data.iterrows():
            # Do formatting for specific tables
            if row.iloc[0] == "Total":
                f.write("\\addlinespace" + " \n")

            f.write(" & ".join([str(x) for x in row.values]) + " \\\\\n")

        f.write("\\hline \n")
        f.write(r"\end{tabular}")

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

    '''
    #print(merged_df)
    comp_df['d_meeting'] = True
    comp_df['articles'] = comp_df['_merge'] == "both"
    comp_df['NYT'] = comp_df['articles'][comp_df['source']=="The New York Times"]
    comp_df['WSJ'] = comp_df['articles'][comp_df['source']=="The Wall Street Journal"]
    comp_df['FT'] = comp_df['articles'][comp_df['source']=="The Financial Times"]
    comp_df['year'] = comp_df['meeting_date'].dt.year
    comp_df = comp_df[['d_meeting', 'NYT','WSJ','FT','year', 'meeting_date']]
    '
    #print(comp_df)
    '''
    return interm_df




main()