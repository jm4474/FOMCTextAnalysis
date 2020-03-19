import pandas as pd
import sys
import os

os.chdir("../output")
interjection_df = pd.read_csv("interjections.csv")
interjection_df = interjection_df[interjection_df.columns[1:]]
#!ls ../../../../../../Replication-file-Robust-Text-Analysis/

separation_df = pd.read_excel("../../../../../../Replication-file-Robust-Text-Analysis/Separation.xlsx")

meeting_df = pd.read_csv("../../../derivation/python/output/meeting_derived_file.csv")

separation_df = separation_df.rename(columns={separation_df.columns[0]:"date_string"})
separation_df.date_string = separation_df.date_string.apply(str)

separation_df['Date'] = pd.to_datetime(separation_df.date_string,format="%Y%m")

interjection_df['Date'] = pd.to_datetime(interjection_df.Date)
interjection_df = interjection_df[(interjection_df.Date>pd.to_datetime("1987-07-31"))&
                                  (interjection_df.Date<pd.to_datetime("2006-02-01"))]


interjection_df['date_string'] = interjection_df.Date.\
    apply(lambda x: x.strftime("%Y%m")).apply(str)


cc_df = meeting_df[meeting_df.event_type=="Meeting"]
cc_df['Date'] = pd.to_datetime(cc_df['end_date'])
interjection_df = interjection_df[interjection_df['Date'].isin(cc_df['Date'])]

print("After removing conference calls, we have {} separation dates and {} interjection dates"
.format(len(set(separation_df.date_string)),len(set(interjection_df.date_string))))
'''
for s_d,i_d in zip(separation_dates,interjection_dates):
    print("Separation:",s_d)
    print("---")
    print("Interjection",i_d)
    print("==="*20)
'''

separation_df['date_ind'] = separation_df.date_string.astype(int)
separation_df = separation_df.set_index('date_ind')

meeting_groups = interjection_df.groupby("Date")
final_df = pd.DataFrame(columns=interjection_df.columns)
for meeting_number,date_ind in enumerate(interjection_df['date_string'].drop_duplicates().astype(int)):
    #print("Currently Working On Date:",date_ind)
    #print("Meeting {} of {}".format(meeting_number,len(interjection_df['date_string'])))
    meeting_date = interjection_df[interjection_df.date_string.astype(int)==date_ind].reset_index(drop=True)
    meeting_date['FOMC_Section'] = 0
    if date_ind not in list(separation_df.index):
        final_df = pd.concat([final_df, meeting_date], ignore_index = True)
        continue
    try:
        meeting_date.loc[separation_df['FOMC1_start'][date_ind]:
                                separation_df['FOMC1_end'][date_ind],"FOMC_Section"] = 1
        #print(FOMC1)
        if separation_df['FOMC2_end'][date_ind] == 'end':
            meeting_date.loc[separation_df['FOMC2_start'][date_ind]:
                            ,"FOMC_Section"] = 2
        else:
            meeting_date.loc[separation_df['FOMC2_start'][date_ind]:
                            separation_df['FOMC2_end'][date_ind],"FOMC_Section"]=2
        #FOMC2 = meeting_date.iloc[separation['FOMC2_start'][date]:]

        final_df = pd.concat([final_df, meeting_date], ignore_index = True)
    except:
        final_df = pd.concat([final_df, meeting_date], ignore_index = True)

print(final_df)

final_df.to_csv("../output/interjections_with_sections.csv")