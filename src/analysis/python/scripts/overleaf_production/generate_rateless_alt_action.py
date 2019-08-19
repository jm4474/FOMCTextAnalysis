import pandas as pd
import matplotlib.pyplot as plt

def main():
    pd.options.mode.chained_assignment = None
    date_partitions = [[pd.to_datetime("1989-08-01")
                           ,pd.to_datetime("2005-07-31")],
                       [pd.to_datetime('1989-08-01')
                           ,pd.to_datetime('2008-12-31')]]
    df = pd.read_csv("../../output/fed_targets_with_alternatives.csv")
    df = df[df.date != "2003-09-15"]
    df.loc[:,'date'] = pd.to_datetime(df.loc[:,'date'])
    for date_partition in date_partitions:
        date_string = "{}_{}".format(date_partition[0].
                                     strftime("%Y-%m-%d"),
                                     date_partition[1].
                                     strftime("%Y-%m-%d"))
        time_df = df[(df.date>date_partition[0])&(df.date<date_partition[1])]
        time_df = plot_graph(time_df,date_string)
        time_df = export_table(time_df,date_string)
        time_df = produce_by_action_table(time_df,date_partition,date_string)
def plot_graph(df,out):
    df.rename(columns={"bluebook_treatment_size_alt_a":"tsa",
                    "bluebook_treatment_size_alt_b":"tsb",
                    "bluebook_treatment_size_alt_c":"tsc",
                    "bluebook_treatment_size_alt_d":"tsd",
                    "bluebook_treatment_size_alt_e":"tse"
                    },inplace=True)
    plt.rc('text', usetex=True)
    fig = plt.figure(figsize=(10, 3))
    fed_target = fig.add_subplot(2, 1, 1)
    df.sort_values(by="date",inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    fed_target.plot(df['date'],df['target_after'])

    action = fig.add_subplot(2,1,2,sharex=fed_target)
    df['tsa'] = pd.to_numeric(df['tsa'],errors="coerce")
    df['tsb'] = pd.to_numeric(df['tsb'],errors="coerce")
    df['tsc'] = pd.to_numeric(df['tsc'],errors="coerce")
    df['tsd'] = pd.to_numeric(df['tsd'],errors="coerce")
    df['tse'] = pd.to_numeric(df['tse'],errors="coerce")

    df.loc[((df['tsa'] < 0)|
            (df['tsb'] < 0)|
            (df['tsc'] < 0)|
            (df['tsd'] < 0)|
            (df['tse'] < 0)),'d_dec'] = -1

    df.loc[((df['tsa'] == 0) |
            (df['tsb'] == 0) |
            (df['tsc'] == 0) |
            (df['tsd'] == 0) |
            (df['tse'] == 0)), 'd_unc'] = 0

    df.loc[((df['tsa'] > 0) |
            (df['tsb'] > 0) |
            (df['tsc'] > 0) |
            (df['tsd'] > 0) |
            (df['tse'] > 0)), 'd_inc'] = 1
    df.loc[df['decision']>0,'effect'] = 1
    df.loc[df['decision']==0,'effect'] = 0
    df.loc[df['decision']<0,'effect'] = -1

    action.plot(df['date'],df['d_dec'],'bo', markersize=1)
    action.plot(df['date'],df['d_unc'],'bo', markersize=1)
    action.plot(df['date'],df['d_inc'],'bo', markersize=1)
    action.plot(df['date'],df['effect'],'yo',markersize=2,fillstyle="none")
    [action.axvline(x=_date,linestyle="--",linewidth=".5",color="grey") for _date in df['date']]
    #print(df)
    plt.savefig('../../output/overleaf_files/fig_rateless_alt_actions_{}.png'.format(out)
                , dpi=300, bbox_inches='tight')
    return df

def export_table(df,out):
    df['options'] = df['d_dec'].apply(lambda x: "E" if x == -1 else "") + \
                    df['d_unc'].apply(lambda x: "U" if x == 0 else "") + \
                    df['d_inc'].apply(lambda x: "T" if x == 1 else "")
    df['E'] = df['effect'].apply(lambda x: 1 if x == -1 else 0)
    df['U'] = df['effect'].apply(lambda x: 1 if x == 0 else 0)
    df['T'] = df['effect'].apply(lambda x: 1 if x == 1 else 0)
    # print(df[['d_dec','d_unc','d_inc',
    #          'sum_dec','sum_unc',
    #          'sum_inc','options','effect']])
    df.to_csv("../../output/action_table.csv")
    grouped = df.groupby("options").sum()
    output = grouped[['E', 'U', 'T']]
    # print(df[df.options==""])
    output.to_latex("../../output/treatment_counts_{}.tex".format(out))
    return df

def produce_by_action_table(df,dates,out):
    merge_df = pd.DataFrame()
    for option in ["E","T","U"]:
        option_df = df[(df.options.str.contains(option))
                       & (df.options.str.len()>1)].\
              groupby("options").sum()
        option_df.reset_index(inplace=True)
        option_df['option'] = option
        option_df = option_df[["option","options","E","T","U"]]
        merge_df = merge_df.append(option_df,ignore_index=True)
    grouped_options = merge_df.groupby("option")
    for name, group in grouped_options:
        group['t_size'] =\
            (group['E']+group['U']+group['T']).sum()
        group['op_size'] = group['E']+group['U']+group['T']
        group = group[["t_size","op_size","options","E","U","T"]]
        group.to_latex("../../output/treatment_counts_action_{}_date_{}"
                                 .format(name,out)
                                 )
        print("{}:  {}".format(name,group.sum(numeric_only=True).sum()))
        print(dates)
        print(group)
        print()
    return df

if __name__ == "__main__":
    main()