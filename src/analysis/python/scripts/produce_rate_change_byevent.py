import pandas as pd
import numpy as np
import datetime
def main():
    pd.options.display.max_rows=10000
    start_date = datetime.datetime(1989, 7, 1)
    end_date=datetime.datetime(2006, 2, 1)
    dates = pd.read_csv("../../../derivation/python/output/meeting_derived_file.csv")
    rates = pd.read_excel("../../../collection/python/data/FRED_DFEDTAR.xls", skiprows=10)
    rates.columns = ['date', 'dfedtar']
    rates['shift'] = rates['dfedtar'].shift(1)
    rates['date'] = pd.to_datetime(rates['date'])
    rates = rates[(start_date <= rates.date) & (rates.date < end_date)]

    rates['change'] = rates['shift'] != rates['dfedtar']
    dates = dates[['end_date', 'event_type']]
    dates['date'] = pd.to_datetime(dates['end_date'])
    merge = pd.merge(rates, dates, on="date", how="left")
    #merge['event_shift'] = merge['event_type'].shift(1)
    merge['month'] = merge.date.dt.month
    merge['year'] = merge.date.dt.year

    merge['meeting'] = (merge['event_type'] == "Meeting")
    merge['sch_conf_call'] = (merge['event_type'] == "Conference Call")


    # Account for the inconsistent recording of the 09/15 - 09/16/2003 Meeting
    merge=merge[merge.date!=datetime.datetime(2003, 9, 15)]

    # Account for the visibility of shifts one day after the meeting before 1994.
    merge.loc[merge.year<1994,'change'] = merge['change'][(merge.year < 1994) 
        & (merge.date!=datetime.datetime(1990, 12, 7))
        & (merge.date!=datetime.datetime(1991, 1, 9))
        & (merge.date!=datetime.datetime(1991, 1, 9))
        & (merge.date!=datetime.datetime(1991, 2, 1)) 
        & (merge.date!=datetime.datetime(1991, 4, 30)) 
        & (merge.date!=datetime.datetime(1991, 4, 30)) 
        & (merge.date!=datetime.datetime(1991, 9, 13))].shift(-1)
    
    merge.loc[(merge.event_type.isna()) & (merge.change==True),'event_type'] = "Intermeeting Change"
    
    pivot = merge[merge.event_type.notna()].pivot_table(values='date',index=['event_type'],columns=['change'], aggfunc=len)
    pivot=pivot.reset_index()

    pivot.rename(columns={"event_type":"Event type"},inplace=True)
    pivot.rename(columns={False:"No Change"},inplace=True)
    pivot.rename(columns={True:"Change"},inplace=True)


    addline={"Event type":"Total"}
    for item in list(pivot.columns)[1:]:
        addline.update({item:pivot[item].sum() })

    pivot=pivot.append(addline,ignore_index=True)
    
    pivot.loc[pivot['No Change'].isna(), 'No Change']=0
    pivot['Events']=pivot['No Change']+pivot['Change']
    pd.options.display.float_format = '{:.0f}'.format
    pivot=pivot.reindex([2,0,1,3])


    output_text = pivot.to_latex(index=False)
    output_text = output_text.replace("Total","\\hline  Total",1)
    output_text = output_text.replace("Events","Total",1)
    #print(output_text)
    with open("../output/overleaf_files/rate_change_byevent.tex",'w+') as f:
        f.write(output_text)


if __name__ == "__main__":
    main()