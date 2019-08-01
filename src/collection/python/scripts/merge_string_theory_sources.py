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

    treasury_yields = pd.read_csv("../data/string_theory/FRB_H15.csv")
    treasury_yields['DATE'] = pd.to_datetime(treasury_yields['Unique Identifier: '],errors="coerce")
    treasury_yields = treasury_yields.dropna(subset=['DATE'])
    treasury_yields['TRY_3M'] = treasury_yields['H15/H15/RIFLGFCM03_N.B']
    treasury_yields['TRY-2Y'] = treasury_yields['H15/H15/RIFLGFCY02_N.B']
    treasury_yields['TRY-10Y'] = treasury_yields['H15/H15/RIFLGFCY10_N.B']
    treasury_yields = treasury_yields[['DATE','TRY_3M','TRY-2Y','TRY-10Y']]

    futures_contract = pd.read_excel("../data/string_theory/federal_funds_cont.xlsx")
    futures_contract['DATE'] = pd.to_datetime(futures_contract.iloc[:,0],errors='coerce')
    futures_contract['FF1_COMDTY'] = futures_contract.iloc[:,1]
    futures_contract['FF2_COMDTY'] = futures_contract.iloc[:,2]
    futures_contract = futures_contract[['DATE','FF1_COMDTY','FF2_COMDTY']]
    futures_contract = futures_contract.dropna(subset=["DATE"])

    dataframes = [dfedtar,dfedtarl,dfedtaru,dff,indpro,pcepi,unrate,treasury_yields,futures_contract]
    for dataframe in dataframes:
        dataframe['DATE'] = pd.to_datetime(dataframe['DATE'])
    df_merged = reduce(lambda left,right: \
                           pd.merge(left,right,on=['DATE'],how='outer'),dataframes)

    df_merged['DATE'] = pd.to_datetime(df_merged['DATE'])
    monthly = df_merged[df_merged['DATE'].dt.day==1]

    df_merged.to_csv("../output/string_theory_indicators_daily.csv")
    monthly.to_csv("../output/string_theory_indicators_monthly.csv")

if __name__ == "__main__":
    main()