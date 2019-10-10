import pandas as pd
def main():
    meeting_info = pd.read_csv("../output/meeting_derived_file.csv")
    meeting_info = meeting_info[['end_date','event_type']]

    control_info = pd.read_csv("../../../collection/python/output/string_theory_indicators_daily_new.csv")

    df_merged = pd.merge(left=control_info,right=meeting_info,left_on='DATE',right_on="end_date",how="left")
    df_merged = df_merged[df_merged.columns[1:]]
    df_merged.to_csv("../output/daily_policy_data.csv")

if __name__ == "__main__":
    main()