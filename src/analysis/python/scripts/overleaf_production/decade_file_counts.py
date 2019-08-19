import pandas as pd
def main():
    df = pd.read_csv("../../../collection/python/output/derived_data.csv")
    df['date'] = pd.to_datetime(df['end_date'])

    df['decade'] = df['date'].dt.year//10*10
    decades = sorted(list(set(df['decade'])))
    for decade in set(df['decade']):
        df[decade] = df['decade'] == decade
    df["File Type"] = df['grouping']
    unique_group = df.drop_duplicates(subset=["end_date","File Type"])
    grouped_docs = unique_group.groupby("File Type")
    grouped_counts = grouped_docs.sum().astype(int)[decades]
    grouped_counts["Total"] = grouped_counts.sum(axis=1)
    print(grouped_counts)
    drop_docs = ["Greenbook and Bluebook accessible materials",
                 "Memos", "Press Conference", "Tealbook accessible materials"
                 ]
    grouped_counts = grouped_counts.drop(drop_docs). \
        rename({"Intermeeting Executive Committee Minutes": "Intermeeting Minutes",
                "SEP":"Economic Projections (SEP)"})
    '''
    columns = {1930:"1936-39",
               1940:"1940-49",
               1950:"1950-59",
               1960:"1960-69",
               1970:"1970-79",
               1980:"1980-89",
               1990:"1990-99",
               2000:"2000-09",
               2010:"2010-13"}
    '''

    grouped_counts = grouped_counts.reset_index()
    headers = ["File Type",
               "\\shortstack{1936-\\\\1939}",
               "\\shortstack{1940-\\\\1949}",
               "\\shortstack{1950-\\\\1959}",
               "\\shortstack{1960-\\\\1969}",
               "\\shortstack{1970-\\\\1979}",
               "\\shortstack{1980-\\\\1989}",
               "\\shortstack{1990-\\\\1999}",
               "\\shortstack{2000-\\\\2010}",
               "\\shortstack{2010-\\\\2013}",
               "Total"]
    #grouped_counts = grouped_counts.rename(columns=columns)
    grouped_counts.to_latex("../output/decade_file_counts.tex",index=False,header=headers,escape=False)


if __name__ == "__main__":
    main()