import pandas as pd
from functools import reduce
def main():
    dfedtar = pd.read_csv("../data/string_theory/DFEDTAR.csv")
    dfedtarl = pd.read_csv("../data/string_theory/DFEDTARL.csv")
    dfedtaru = pd.read_csv("../data/string_theory/DFEDTARU.csv")
    dff = pd.read_csv("../data/string_theory/DFF.csv")
    indpro = pd.read_csv("../data/string_theory/INDPRO.csv")
    pcepi = pd.read_csv("../data/string_theory/PCEPI.csv")
    unrate = pd.read_csv("../data/string_theory/UNRATE.csv")

    dataframes = [dfedtar,dfedtarl,dfedtaru,dff,indpro,pcepi,unrate]

    df_merged = reduce(lambda left,right: \
                           pd.merge(left,right,on=['DATE'],how='outer'),dataframes)

    df_merged['DATE'] = pd.to_datetime(df_merged['DATE'])
    monthly = df_merged[df_merged['DATE'].dt.day==1]

    df_merged.to_csv("../output/string_theory_indicators_daily.csv")
    monthly.to_csv("../output/string_theory_indicators_monthly.csv")

if __name__ == "__main__":
    main()