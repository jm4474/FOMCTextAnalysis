import pandas as pd
def main():
    meeting_info = pd.read_csv("../../../analysis/python/output/alternative_treatment_decisions.csv")
    controls = pd.read_csv("../../../collection/python/output/string_theory_indicators_monthly.csv")
    controls['month'] = pd.to_datetime(controls['DATE'])

    meeting_info['month'] = pd.to_datetime(meeting_info['end_date'])
    meeting_info['month'] = meeting_info['month'].apply(lambda dt:dt.replace(day=1))
    merged_df = pd.merge(left=controls,right=meeting_info,on="month")
    merged_df = merged_df[[
        'month','statement_policy_change','bluebook_treatment_size_alt_a',
        'bluebook_treatment_size_alt_b','bluebook_treatment_size_alt_c',
        'UNRATE','PCEPI','INDPRO','end_date','event_type'
    ]]
    merged_df['end_date'] = 'meeting_end_date'

    merged_df.to_csv("../output/monthly_policy_data.csv")



if __name__ == "__main__":
    main()