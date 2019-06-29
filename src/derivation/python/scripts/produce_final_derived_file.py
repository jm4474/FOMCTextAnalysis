import pandas as pd
#MERGES TOGETHER DATA FROM ALL SOURCES TO PRODUCE A FINAL DERIVED FILE
def main():
    derived_df = pd.read_csv("../../../collection/python/output/derived_data.csv")
    print(len(derived_df))
    der_state_df = merge_statement(derived_df)
    print(len(der_state_df))
    der_state_ftr_df = merge_ftr(der_state_df)
    print(len(der_state_ftr_df))
    der_state_ftr_nyt_df = merge_news(der_state_ftr_df)
    print(len(der_state_ftr_nyt_df))
    der_state_ftr_nyt_bb_df = merge_bluebook(der_state_ftr_nyt_df)
    print(len(der_state_ftr_nyt_bb_df))
    der_state_ftr_nyt_bb_df.to_csv("../output/final_derived_file.csv")
def merge_statement(cur_df):
    print("merging statements")
    statement_df = pd.read_csv("../output/statements_text_extraction.csv")
    cur_df = cur_df.drop_duplicates(subset="start_date")
    cur_df = cur_df[['start_date','end_date','event_type']]
    #print(len(cur_df))
    statement_df = statement_df[['meeting_start_date','policy_change','policy_action']]
    statement_df = statement_df.add_prefix("statement_")
    statement_df['start_date'] = statement_df['statement_meeting_start_date']
    statement_df = statement_df.drop('statement_meeting_start_date',axis=1)
    #print(statement_df)
    assert(len(statement_df)<len(cur_df))
    merge_statment = cur_df.merge(statement_df,how="left",on="start_date")
    #print(merge_statment)
    #print(merge_statment.columns)
    return merge_statment
def merge_ftr(cur_df):
    print("mergeing futures")
    future_df = pd.read_csv("../output/federal_funds_futures.csv")
    #FFR Column is FF0 after adjusting for date
    future_df['start_date'] = future_df['date']
    future_df = future_df.drop('date',axis=1)
    future_df["FFF_0_rate"] = future_df["ffr_future"]
    future_df = future_df.drop("ffr_future",axis=1)
    merge_ftr = cur_df.\
        merge(future_df,on="start_date",how="left")

    #print(merge_ftr)
    #print(merge_ftr.columns)
    return merge_ftr

def merge_news(cur_df):
    print("merging news")
    news_df = pd.read_csv("../../../derivation/python/output/all_news_articles.csv")

    number_articles = len(news_df)
    #print("We currently have {} articles".format(number_articles))
    #print("Out of those, we have {} valid articles".format(len(valid_articles)))
    # print(nyt_df.sort_values(by="article_date"))
    for news_source in news_df['source'].unique():
        column_name_parts = (news_source.strip("The ").lower()).split()
        count_column_name = ("".join(word[0] for word in column_name_parts)) +"_article_count"
        cur_news_df = news_df[news_df.source==news_source]
        valid_articles = cur_news_df[cur_news_df['content'] != ""]
        value_counts = valid_articles.meeting_date.value_counts(dropna=True, sort=True)
        df_value_counts = pd.DataFrame(value_counts)
        df_value_counts = df_value_counts.reset_index()
        df_value_counts.columns = ['end_date', count_column_name]
        cur_df['end_date'] = pd.to_datetime(cur_df['end_date'])
        df_value_counts['end_date'] = pd.to_datetime(df_value_counts['end_date'])
        cur_df = cur_df.merge(df_value_counts,on="end_date",how="left")
        cur_df[count_column_name].fillna(0,inplace=True)
    return cur_df

def merge_bluebook(cur_df):
    print("merging bluebook")
    blue_df = pd.read_excel("../../../analysis/python/data/bluebook_manual_data_online_WORKING.xlsx")
    blue_df['start_date'] = pd.to_datetime(blue_df['start_date'])
    orig_columns = ['start_date','DFF_Before_meeting','DFEDTR_before',
               'DFEDTR_end','C_TREATMENT_alt_a','C_TREATMENT_SIZE_alt_a',
               'justify_alt_a', 'C_TREATMENT_alt_b','C_TREATMENT_SIZE_alt_b',
               'justify_alt_b', 'C_TREATMENT_alt_c','C_TREATMENT_SIZE_alt_c',
               'justify_alt_c', 'C_TREATMENT_alt_d','C_TREATMENT_SIZE_alt_d',
               'justify_alt_d', 'C_TREATMENT_alt_e', 'C_TREATMENT_SIZE_alt_e',
               'justify_alt_e', 'comments']
    blue_df = blue_df[orig_columns]
    new_cols = ['start_date','DFF_Before_meeting','DFEDTR_before',
               'DFEDTR_end','bluebook_treatment_alt_a','bluebook_treatment_size_alt_a',
               'bluebook_justify_alt_a', 'bluebook_treatment_alt_b','bluebook_treatment_size_alt_b',
               'bluebook_justify_alt_b', 'bluebook_treatment_alt_c','bluebook_treatment_size_alt_c',
               'bluebook_justify_alt_c', 'bluebook_treatment_alt_d','bluebook_treatment_size_alt_d',
               'bluebook_justify_alt_d', 'bluebook_treatment_alt_e','bluebook_treatment_size_alt_e',
               'bluebook_justify_alt_e', 'bluebook_comments']
    blue_df.columns = new_cols
    cur_df['start_date'] = pd.to_datetime(cur_df['start_date'])

    merge_bluebook = cur_df.merge(blue_df,on="start_date",how="left")

    return merge_bluebook

main()