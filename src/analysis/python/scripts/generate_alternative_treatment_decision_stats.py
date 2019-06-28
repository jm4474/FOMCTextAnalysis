import pandas as pd
import numpy as np
def main():
    df = pd.read_csv("../output/alternative_treatment_decisions.csv")

    df = df[df.columns[1:]]
    df = df[df.statement_policy_action.notnull()]
    df = df[df.bluebook_treatment_alt_a.notnull()]
    df['policy_options'] = df.apply(lambda row: get_policy_options(row),axis=1)
    #print(df)
    pivot = pd.pivot_table(data=df,index="policy_options",columns="statement_policy_action",
                           values="end_date",aggfunc=np.count_nonzero,fill_value=0)
    pivot = pivot.reset_index()
    pivot.rename(columns={"policy_options": "policy menu"}, inplace=True)
    pivot = pivot.append({'policy menu': 'Total', 'E': pivot['E'].sum()\
                          ,'T': pivot['T'].sum(),'U': pivot['U'].sum()\
                          }, ignore_index=True)
    print(pivot.columns)
    print(pivot)


    create_table_df(pivot,"policy_alternative_decisions")
def get_policy_options(row):
    policy_options = []
    for alternative in ['bluebook_treatment_alt_a','bluebook_treatment_alt_b','bluebook_treatment_alt_c']:
        if str(row[alternative]) in ['U','T','E','?']:
            policy_options += (row[alternative])
    policy_options = sorted(policy_options)
    return ' '.join(policy_options)


def create_table_df(data, name):
    columnheaders = list(data.columns)
    numbercolumns = len(columnheaders)

    with open("../output/" + name + ".tex", "w") as f:
        f.write(r"\begin{tabular}{" + "l" + "".join("c" * (numbercolumns - 1)) + "}\n")
        f.write("\\hline\\hline \n")
        f.write("\\addlinespace" + " \n")
        f.write(" & ".join([str(x) for x in columnheaders]) + " \\\ \n")
        f.write("\\hline \n")
        # write data
        for idx, row in data.iterrows():
            # Do formatting for specific tables
            if row.iloc[0] == "Total":
                f.write("\\addlinespace" + " \n")

            f.write(" & ".join([str(x) for x in row.values]) + " \\\\\n")

        f.write("\\hline \n")
        f.write(r"\end{tabular}")

main()