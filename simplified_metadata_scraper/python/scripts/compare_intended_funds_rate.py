import pandas as pd

def main():
    events = {}
    oliver_df = pd.read_csv("../output/statements_text_extraction_cleaned.csv")
    romer_df = pd.read_csv("../output/romer_data.csv")
    daily_data_df = pd.read_csv("../../Matlab/Output/Bluebook/CSV/SentencesC.csv",encoding="ISO-8859-1")

    daily_data_df['date'] = pd.to_datetime(daily_data_df['start_date'])
    romer_df['date'] = pd.to_datetime(romer_df['date'])
    oliver_df['date'] = pd.to_datetime(oliver_df['date'])

    oliver_merge_daily = pd.merge(daily_data_df, oliver_df, on="date")
    oliver_merge_romer = pd.merge(oliver_df, romer_df, on="date")
    daily_merge_romer = pd.merge(daily_data_df, romer_df, on="date")

    oliver_comp_daily = oliver_merge_daily.filter(['date','DFF_Before_meeting',
                                                   'target_before','DFEDTR',
                                                   'target_after'
                                                   ])
    oliver_comp_romer = oliver_merge_romer.filter(['date','prev','target_before',
                                                   'new','target_after'
                                                   ])
    daily_comp_romer = daily_merge_romer.filter(['date', 'DFF_Before_meeting',
                                                  'prev','DFEDTR'
                                                     , 'new'
                                                   ])
    oliver_comp_daily.to_csv("../output/oliver_comp_daily.csv")
    oliver_comp_romer.to_csv("../output/oliver_comp_romer.csv")
    daily_comp_romer.to_csv("../output/daily_comp_romer.csv")
    print(oliver_comp_daily)
    print(oliver_comp_romer)
    print(daily_comp_romer)
main()