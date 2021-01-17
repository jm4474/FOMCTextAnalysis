import pandas as pd
from functools import reduce
import re
import os
import numpy as np
import requests

PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/economic_data") 
GR_PATH = os.path.expanduser("~/Dropbox/MPCounterfactual/src/collection/python/output")


# =============================================================================
### daily ###

dfedtar = pd.read_csv(f"{PATH}/raw_data/DFEDTAR.csv")
dfedtarl = pd.read_csv(f"{PATH}/raw_data/DFEDTARL.csv")
dfedtaru = pd.read_csv(f"{PATH}/raw_data//DFEDTARU.csv")
dff = pd.read_csv(f"{PATH}/raw_data//DFF.csv")


# =============================================================================
### monthly ###
def m_import(path):
    data = pd.read_csv(path)
    data["DATE"] = pd.to_datetime(data["DATE"])
    data["year"] = data["DATE"].dt.year
    data["month"] = data["DATE"].dt.month
    data = data[data["year"]>1980].copy()
    data.drop(columns=["DATE"],inplace=True)
    data = data.set_index(["year","month"])
    return data
    
# Industrial Production Index
indpro = m_import(f"{PATH}/raw_data/INDPRO.csv")

# Personal Consumption Expenditures: Chain-type Price Index (PCEPI)
pcepi = m_import(f"{PATH}/raw_data/PCEPI.csv")

# Unemployment Rate (UNRATE)
unrate = m_import(f"{PATH}/raw_data/UNRATE.csv")

#merge
data_m = pd.concat([indpro,pcepi,unrate],axis=1)
data_m = data_m.reset_index()

data_m["UNRATE"] = data_m["UNRATE"] / 100
data_m["d_UNRATE"] = data_m["UNRATE"].diff(periods=1)
data_m["l1d_UNRATE"] = data_m["d_UNRATE"].shift(periods=1)
data_m["l2d_UNRATE"] = data_m["d_UNRATE"].shift(periods=2)

data_m["ln_INDPRO"] = np.log(data_m["INDPRO"])
data_m["dln_INDPRO"] = data_m["ln_INDPRO"].diff(periods=1)
data_m["l1dln_INDPRO"] = data_m["dln_INDPRO"].shift(periods=1)
data_m["l2dln_INDPRO"] = data_m["dln_INDPRO"].shift(periods=2)

data_m["ln_PCEPI"] = np.log(data_m["PCEPI"])
data_m["dln_PCEPI"] = data_m["ln_PCEPI"].diff(periods=1)
data_m["l1dln_PCEPI"] = data_m["dln_PCEPI"].shift(periods=1)
data_m["l2dln_PCEPI"] = data_m["dln_PCEPI"].shift(periods=2)

# =============================================================================

### Greenbook data ###
from datequarter import DateQuarter

gr_data = pd.read_csv(f"{GR_PATH}/greenbook_data.csv")

gr_data["meeting_date"] = pd.to_datetime(gr_data["meeting_date"],format='%Y%m%d')
gr_data["meeting_year"] = gr_data["meeting_date"].dt.year
gr_data["meeting_quarter"] = gr_data["meeting_date"].dt.quarter
gr_data["meeting_quarterly"] = gr_data["meeting_date"].apply(lambda x: DateQuarter(x.year,x.quarter))

gr_data["forecast_date"] = gr_data["forecast_date"].apply(lambda x: f'{str(x).split(".")[0]}-{int(str(x).split(".")[1])*3:02d}-01')
gr_data["forecast_date"] = pd.to_datetime(gr_data["forecast_date"],format='%Y-%m-%d')
gr_data["forecast_year"] = gr_data["forecast_date"].dt.year
gr_data["forecast_quarter"] = gr_data["forecast_date"].dt.quarter

gr_data["relforecast_quarter"] = gr_data[["meeting_year","meeting_quarter","forecast_year","forecast_quarter"]].apply(
    lambda x: DateQuarter(x["meeting_year"],x["meeting_quarter"]) - DateQuarter(x["forecast_year"],x["forecast_quarter"]) , axis=1)

variables = list(gr_data["macro_variable"].unique())
meeting_dates = list(gr_data["meeting_date"].unique())

table = gr_data.pivot_table(index=["meeting_date"],values="projection",columns=["macro_variable",'relforecast_quarter'])
newcols = [ f'{col[0]}_{str(col[1]).replace("-","l")}'  for col in table.columns]
table.columns = newcols

# replace l1 with 0 if l1 is mssing
for var in variables:
    table.loc[table[f"{var}_l1"].isna(),f"{var}_l1"] = table.loc[table[f"{var}_l1"].isna(),f"{var}_0"]    

table.to_pickle("final_data/greenbook_data.pkl")


table.to_stata("final_data/greenbook_data.dta",convert_dates={"meeting_date":"td"})

### Add financial indicators ###
    
    # Treasury Yields

# Download Data from here:
# =============================================================================
# url = "https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv"
# r = requests.get(url)
# r.status_code
# with open(f'{PATH}/raw_data/fed_zerobondyields.csv', 'wb') as f:
#     f.write(r.content)
# # Pre-process the data
# =============================================================================
start_date = "1971-11-01"
end_date = "2020-9-30"

currentyear = end_date

df = pd.read_csv(f'{PATH}/raw_data/fed_zerobondyields.csv',skiprows=9)

df["date"] = pd.to_datetime(df["Date"])

df = df[(df["date"]>=start_date) & (df["date"]<=end_date) ]
df = df[~df["BETA0"].isna()]

df["month"] = df["date"].dt.month
df["year"] = df["date"].dt.year
df["day"] = df["date"].dt.day
eom = df.groupby(["year","month"])["date"].max().reset_index().rename(columns={"date":"eom"})
df = df.merge(eom,on=["year","month"],how="inner")

data = df.copy()
data = data[["date","year","month"]+["SVENY{:02.0f}".format(x) for x in range(1,11)]+["day"]]
# Express in percentage
for mat in range(1,11):
    data["SVENY{:02.0f}".format(mat)] =     data["SVENY{:02.0f}".format(mat)] / 100
treasury_df = data.copy()
treasury_df = treasury_df.set_index("date")
del data
del df

    # Credit Spreads
mood_aaa = pd.read_csv(f"{PATH}/raw_data/AAA10Y.csv")
mood_aaa["DATE"] = pd.to_datetime(mood_aaa["DATE"])
mood_aaa[mood_aaa["AAA10Y"]=="."] = np.nan
mood_aaa.fillna(method="ffill",inplace=True)
mood_aaa["AAA10Y"] = pd.to_numeric(mood_aaa["AAA10Y"])
mood_aaa["AAA10Y"] = mood_aaa["AAA10Y"].apply(lambda x: x/100)
mood_aaa = mood_aaa.drop_duplicates(subset="DATE",keep="first")
mood_aaa = mood_aaa.set_index(["DATE"])

mood_baa = pd.read_csv(f"{PATH}/raw_data/BAA10Y.csv")
mood_baa["DATE"] = pd.to_datetime(mood_baa["DATE"])
mood_baa[mood_baa["BAA10Y"]=="."] = np.nan
mood_baa.fillna(method="ffill",inplace=True)
mood_baa["BAA10Y"] = pd.to_numeric(mood_baa["BAA10Y"])
mood_baa["BAA10Y"] = mood_baa["BAA10Y"] / 100
mood_baa = mood_baa.drop_duplicates(subset="DATE",keep="first")
mood_baa = mood_baa.set_index(["DATE"])

cd_df = pd.concat([mood_aaa,mood_baa],axis=1)


    # Equity Returns
sandp500 = pd.read_csv(f"{PATH}/raw_data/sandp500.csv")
sandp500["date"] = pd.to_datetime(sandp500["caldt"],format='%Y%m%d')
sandp500.drop(columns = ["caldt"] ,inplace=True)
sandp500 = sandp500.set_index("date")

marketreturns = pd.read_csv(f"{PATH}/raw_data/marketreturns.csv")    
marketreturns["date"] = pd.to_datetime(marketreturns["caldt"],format='%Y%m%d')
marketreturns.drop(columns = ["caldt"] ,inplace=True)

marketreturns = marketreturns.set_index("date")

    # Liquidity - TED Spread
tedspread = pd.read_csv(f"{PATH}/raw_data/TEDRATE.csv")
tedspread["DATE"] = pd.to_datetime(tedspread["DATE"])
tedspread[tedspread["TEDRATE"]=="."] = np.nan
tedspread.fillna(method="ffill",inplace=True)
tedspread["TEDRATE"] = pd.to_numeric(tedspread["TEDRATE"])
tedspread["TEDRATE"] = tedspread["TEDRATE"] / 100
tedspread = tedspread.drop_duplicates(subset="DATE",keep="first")
tedspread = tedspread.set_index(["DATE"])

    # Daily Market Data
market_d = pd.concat([treasury_df,cd_df,sandp500,marketreturns,tedspread],axis=1)
market_d = market_d[(market_d.index>"1980-01-01") & (market_d.index<"2019-12-31")]
market_d.drop(columns=["year", "month"],inplace=True)
market_d["month"] = market_d.index.month
market_d["year"] = market_d.index.year
market_d = market_d.reset_index()

    # Equity Valuations
cape = pd.read_excel(f"{PATH}/raw_data/schiller_cape.xls",sheet_name = "Data",skiprows=4,header=[0,1,2,3])
cape.columns = ["_".join(col) for col in cape.columns]
cape = cape[['Unnamed: 0_level_0_Unnamed: 0_level_1_Unnamed: 0_level_2_Date','Earnings_Ratio_P/E10 or_CAPE']].copy()
cape.rename(columns={'Unnamed: 0_level_0_Unnamed: 0_level_1_Unnamed: 0_level_2_Date':"date",'Earnings_Ratio_P/E10 or_CAPE':"m_cape"},inplace=True)
cape = cape[~cape["date"].isna()].copy()
cape["date"] = cape["date"].apply(lambda x: str(x) if str(x).split(".")[1]!="1" else f"{str(x).split('.')[0]}.10")
cape["date"] = cape["date"].apply(lambda x: f'{str(x).split(".")[0]}-{int(str(x).split(".")[1]):02d}-01')

cape["date"] = pd.to_datetime(cape["date"],format='%Y-%m-%d')
cape["year"] = cape["date"].dt.year
cape["month"] = cape["date"].dt.month
cape = cape[(cape["year"]>=1980) & (cape["year"]<2020)].copy()

total_market = market_d.merge(cape,on=["year", "month"],how="outer")
total_market.drop(columns=["day","date"],inplace=True)
total_market.rename(columns={"index":"date"},inplace=True)

for col in [cl for cl in total_market.columns if cl not in ["date","month","year"]]:
    total_market[col].fillna(method="ffill",inplace=True) 
    
total_market.to_pickle("final_data/marketdata.pkl")

# =============================================================================
### Merge all the data

start_date = np.datetime64("1985-01-01")
end_date = np.datetime64("2015-12-31")
index = pd.date_range(start_date, end_date, freq='D')
 
df = pd.DataFrame(index=index).reset_index().rename(columns={"index":"date"})
df = df.merge(total_market,on="date",how="left")

df = df.merge(data_m,on=["year", "month"],how="left")

dates = pd.read_csv(f"{GR_PATH}/derived_data.csv")
dates["d_meeting"] = 1
dates = dates.drop_duplicates(subset="start_date")
dates["start_date"] = pd.to_datetime(dates["start_date"])
df = df.merge(dates[["d_meeting", "start_date"]],left_on = "date", right_on = "start_date", how= "left")
df.drop(columns=['sprtrn', 'vwretd', 'vwindd',"start_date"],inplace=True)

### Define one and two week and yield differences and returns
for col in ['spindx','vwindx']:
    df[f"{col}"].ffill(inplace=True)
    df[f"ln_{col}"] = np.log(df[f"{col}"])
    df[f"d14ln_{col}"] = df[f"ln_{col}"].diff(periods=14)
    df[f"d28ln_{col}"] = df[f"ln_{col}"].diff(periods=28)
    df[f"d7ln_{col}"] = df[f"ln_{col}"].diff(periods=7)

for col in ['SVENY01', 'SVENY02', 'SVENY03', 'SVENY04', 'SVENY05',
       'SVENY06', 'SVENY07', 'SVENY08', 'SVENY09', 'SVENY10', 'AAA10Y',
       'BAA10Y']:
    df[f"{col}"].ffill(inplace=True)
    df[f"d14_{col}"] = df[f"{col}"].diff(periods=14)
    df[f"d28_{col}"] = df[f"{col}"].diff(periods=28)
    df[f"d7_{col}"] = df[f"{col}"].diff(periods=7)
    

df.to_stata("final_data/econmarketdata.dta",convert_dates={"date":"td"})
df.to_pickle("final_data/econmarketdata.pkl")
            
# =============================================================================
# 
# def main():
# 
#     monthly_dataframes = [indpro,pcepi,pcepi_ch,unrate,pcepi_pch]
#     for dataframe in monthly_dataframes:
#         dataframe['DATE'] = pd.to_datetime(dataframe['DATE'].apply(year_fix))
#         print(dataframe)
#     monthly_merged = reduce(lambda left,right: \
#                            pd.merge(left,right,on=['DATE'],how='outer'),monthly_dataframes)
#     monthly_merged.to_csv("../output/string_theory_indicators_monthly.csv")
# 
#     treasury_yields = pd.read_csv("../data/string_theory/FRB_H15.csv")
#     treasury_yields['DATE'] = pd.to_datetime(treasury_yields['Unique Identifier: '],errors="coerce")
#     treasury_yields = treasury_yields.dropna(subset=['DATE'])
#     treasury_yields['TRY_3M'] = treasury_yields['H15/H15/RIFLGFCM03_N.B']
#     treasury_yields['TRY-2Y'] = treasury_yields['H15/H15/RIFLGFCY02_N.B']
#     treasury_yields['TRY-10Y'] = treasury_yields['H15/H15/RIFLGFCY10_N.B']
#     treasury_yields = treasury_yields[['DATE','TRY_3M','TRY-2Y','TRY-10Y']]
# 
#     futures_contract = pd.read_excel("../data/string_theory/federal_funds_cont.xlsx")
#     futures_contract['DATE'] = pd.to_datetime(futures_contract.iloc[:,0],errors='coerce')
#     futures_contract['FF1_COMDTY'] = futures_contract.iloc[:,1]
#     futures_contract['FF2_COMDTY'] = futures_contract.iloc[:,2]
#     futures_contract = futures_contract[['DATE','FF1_COMDTY','FF2_COMDTY']]
#     futures_contract = futures_contract.dropna(subset=["DATE"])
# 
#     dataframes = [dfedtar,dfedtarl,dfedtaru,dff,treasury_yields,futures_contract]
#     for dataframe in dataframes:
#         dataframe['DATE'] = pd.to_datetime(dataframe['DATE'])
#     df_merged = reduce(lambda left,right: \
#                            pd.merge(left,right,on=['DATE'],how='outer'),dataframes)
# 
#     df_merged['DATE'] = pd.to_datetime(df_merged['DATE'])
# 
#     df_merged.to_csv("../output/string_theory_indicators_daily_new.csv")
# 
# def year_fix(d_str):
#     date = d_str.rsplit("/",1) 
#     if len(date)>1:
#         if int(date[1])>30:
#             return date[0]+"/19"+date[1]
#         else:
#             return date[0]+'/20'+date[1]
#     else:
#         return d_str
# if __name__ == "__main__":
#     main()
# =============================================================================
