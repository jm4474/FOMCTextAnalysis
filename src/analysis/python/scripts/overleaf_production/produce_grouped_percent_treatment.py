import pandas as pd
import numpy as np
import pprint
def main():
    
    sample_startdate=datetime.datetime(1989, 7, 1)
    sample_enddate=datetime.datetime(2006, 2, 1)
   
    raw(sample_startdate,sample_enddate)
    #linearity()
    #symmetry()
def linearity():
    df = pd.read_csv("../../output/monthly_treatment_counts.csv")
    df = df[df.date!="0"]
    cols = ['d_m025', 'd_0', 'd_025']
    df['d_025'] = (df["d_050"] + df["d_075"]+df['d_025']).astype(bool).astype(int)
    df['d_m025'] = (df["d_m050"] + df["d_m075"]+df['d_m025']).astype(bool).astype(int)
    new_df = df.copy()
    mappings = {
        'd_m025':'-0.25',
        'd_0':'0',
        'd_025':'0.25',
    }
    for i in new_df.index:
        bucket = set()
        for col in cols:
            if new_df.loc[i,col]==1:
                bucket.add(mappings[col])
        bucket_str = ",".join(sorted(list(bucket)))
        new_df.loc[i, 'perc_group'] = bucket_str
    targets = pd.read_csv("../output/fed_targets_with_alternatives.csv")[[
        'date', 'decision']]
    targets.loc[168, 'decision'] = -.5
    decisions = set(targets['decision'])
    group_cols = []
    for decision in decisions:
        targets[str(decision)] = targets['decision'] == decision
        #targets[str(decision)] = targets['decision'].apply(lambda x:1 if round_quarter(x)==decision else 0)
        group_cols.append(decision)
    new_df = pd.merge(left=new_df,right=targets,on="date")
    new_df.to_csv("../output/grouped_percent_treatments_linearity.csv")
    new_df['count'] = 1
    #print(new_df.columns)
    group_cols = ['date','perc_group','count']+[str(x) for x in sorted(group_cols)]
    lat_df = new_df.groupby("perc_group")[group_cols].sum()

    #print(lat_df)
    lat_df.to_latex("../output/linearity_percentage_group_counts_no_rounding.tex")


def symmetry():
    df = pd.read_csv("../output/monthly_treatment_counts.csv")
    df = df[df.date!="0"]
    #print(df)
    cols = ['d_m050','d_m025','d_0','d_025','d_050']
    df['d_050'] = (df["d_050"]+df["d_075"]).astype(bool).astype(int)
    df['d_m050'] = (df["d_m050"]+df["d_m075"]).astype(bool).astype(int)

    mappings = {
        'd_m050':50,
        'd_m025':25,
        'd_0':0,
        'd_025':25,
        'd_050':50
    }
    new_df = df.copy()
    for i in new_df.index:
        bucket = set()
        for col in cols:
            if new_df.loc[i,col]==1:
                bucket.add(str(mappings[col]))
        bucket_str = ",".join(sorted(list(bucket)))
        new_df.loc[i,'perc_group'] = bucket_str
        new_df.loc[:,'perc_group'] = new_df['perc_group'].\
            apply(lambda x:"0,25" if x=="25,50" else x)
    new_df['count'] = 1
    targets = pd.read_csv("../output/fed_targets_with_alternatives.csv")[[
        'date','target_before','target_after']]
    targets['decision'] = abs(targets['target_after']-targets['target_before'])
    targets.loc[168,'decision'] = .5
    #print(new_df[new_df.perc_group=="0,25,50"])
    decisions = set(targets['decision'])
    for decision in decisions:
        targets[str(decision)] = targets['decision']
    #    targets[str(decision)] = targets['decision'].apply(lambda x:1 if round_quarter(x)==decision else 0)
    columns = [str(x) for x in decisions]
    columns = columns+['date','decision']
    new_df = pd.merge(left=new_df,right=targets,on="date")
    #print(new_df.columns)
    new_df.to_csv("../output/grouped_percent_treatments_symmetry.csv")
    group_cols = ['date','perc_group','count','0.0','0.25','0.5']
    lat_df = new_df[group_cols].groupby("perc_group").sum()

    #print(lat_df)
    lat_df.to_latex("../output/symmetry_percentage_group_counts.tex")
def raw(sample_startdate,sample_enddate):
    df = pd.read_csv("../../output/monthly_treatment_counts.csv")
    df = df[df.date!="0"]
    cols = ['d_m075','d_m050','d_m025','d_0','d_025','d_050','d_075']
    #df['d_025'] = (df["d_050"] + df["d_075"]+df['d_025']).astype(bool).astype(int)
    #df['d_m025'] = (df["d_m050"] + df["d_m075"]+df['d_m025']).astype(bool).astype(int)
    new_df = df.copy()
    mappings = {
        'd_m075': '-0.75',
        'd_m050': '-0.5',
        'd_m025': '-0.25',
        'd_0': '0',
        'd_025': '0.25',
        'd_050': '0.50',
        'd_075': '-0.75',
    }
    for i in new_df.index:
        bucket = set()
        for col in cols:
            if new_df.loc[i,col]==1:
                bucket.add(mappings[col])
        bucket_str = ",".join(sorted(list(bucket)))
        new_df.loc[i, 'perc_group'] = bucket_str
    targets = pd.read_csv("../../output/fed_targets_with_alternatives.csv")[[
        'date', 'decision']]
    
    targets['newdate']=pd.to_datetime(targets['date'])
    targets=targets[(targets['newdate']>=sample_startdate) & (targets['newdate']<=sample_enddate)]
    targets=targets[targets['newdate']!=datetime.datetime(2003, 9, 15)]
    decisions = set(targets['decision'])
    group_cols = []
    for decision in decisions:
        targets[str(decision)] = targets['decision']==decision
        group_cols.append(decision)
    new_df = pd.merge(left=new_df,right=targets,on="date")
    new_df.to_csv("../../output/grouped_percent_treatments_no_round.csv")
    new_df['count'] = 1
    columns = ['date','perc_group','count']+[str(x) for x in sorted(group_cols)]
    lat_df = new_df.groupby("perc_group")[columns].sum()
    lat_df = lat_df.astype(int).reset_index().rename({"perc_group":"Menu"})
    #print(lat_df)
    lat_df.rename(columns={'perc_group':'Policy Options'},inplace=True)
    lat_df.rename(columns={'count':'Count'},inplace=True)
    lat_df.to_latex("../../output/overleaf_files/percentage_group_counts.tex",index=False)


def round_quarter(val):
    mappings = {
        -.125:-.25,
        .125:.25,
        -.3125:-.25,
        .3125:.25,
        .0625:0,
        -.0625:0,
        .75:.5,
        -.75:-.5
    }
    if val in mappings:
        return mappings[val]
    else:
        return val
if __name__ == "__main__":
    main()