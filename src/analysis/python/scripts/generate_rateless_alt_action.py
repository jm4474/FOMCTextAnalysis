import pandas as pd
import matplotlib.pyplot as plt

def df():
    df = pd.read_csv("../output/fed_targets_with_alternatives.csv")
    df.rename(columns={"bluebook_treatment_size_alt_a":"tsa",
                    "bluebook_treatment_size_alt_b":"tsb",
                    "bluebook_treatment_size_alt_c":"tsc"
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
    df['target_before'] = pd.to_numeric(df['target_before'],errors="coerce")
    df['target_after'] = pd.to_numeric(df['target_after'],errors="coerce")
    df.loc[((df['tsa'] < 0) \
                           | (df['tsb'] < 0) | \
                           (df['tsc'] < 0)),'d_dec'] = -1

    df.loc[((df['tsa'] == 0) \
                           | (df['tsb'] == 0) | \
                           (df['tsc'] == 0)),'d_unc'] = 0

    df.loc[((df['tsa'] > 0) \
                           | (df['tsb'] > 0) | \
                           (df['tsc'] > 0)),'d_inc'] = 1
    df.loc[df['target_after']-df['target_before']>0,'effect'] = 1
    df.loc[df['target_after']-df['target_before']==0,'effect'] = 0
    df.loc[df['target_after']-df['target_before']<0,'effect'] = -1

    action.plot(df['date'],df['d_dec'],'bo', markersize=1)
    action.plot(df['date'],df['d_unc'],'bo', markersize=1)
    action.plot(df['date'],df['d_inc'],'bo', markersize=1)
    action.plot(df['date'],df['effect'])
    [action.axvline(x=_date,linestyle="--",linewidth=".5",color="grey") for _date in df['date']]
    print(df)
    plt.savefig('../output/fig_rateless_alt_actions_line_chart.png', dpi=300, bbox_inches='tight')


if __name__ == "__main__":
    df()