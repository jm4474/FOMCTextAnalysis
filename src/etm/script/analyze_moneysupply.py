import pprint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from fuzzywuzzy import fuzz
from fredapi import Fred
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import requests
import xlrd

pd.options.display.max_colwidth = 60

# FRED API
# fred = Fred(api_key='1b95d612f779c299e0a3cc9b5a3aa8fd')

rel_path = "~/Dropbox/AggregateDemandInflation"
mptext = "~/Dropbox/MPCounterfactual"


# =============================================================================

def import_data(rel_path = "~/Dropbox/AggregateDemandInflation"):
        ### Meetings
    dates = pd.read_pickle("/Users/olivergiesecke/Dropbox/MPCounterfactual/src/analysis/python/output/speaker_data_full.pkl")
    meetingdates = dates.loc[dates["start_date"]>"2006-01-01","start_date"].unique()
    
        ### QE Dates
    qe_dic = {"LSAP" : np.datetime64("2008-11-25"),
              "QE1" : np.datetime64("2009-03-18"),
              "QE2": np.datetime64("2010-11-03"),
              "QE3" : np.datetime64("2011-09-21"),
              "QE4" :np.datetime64("2013-05-22")} 
    
        ### IV Indices
    cols = [['date', '3MTH IMPVOL 80%MNY DF '], ['date.1', '3MTH IMPVOL 90.0%MNY DF'],
           ['date.2', ' 3MTH IMPVOL 95.0%MNY DF'], ['date.3',' 3MTH IMPVOL 97.5%MNY DF '],
           ['date.4', '3MTH IMPVOL 100.0%MNY DF '],
           ['date.5', '3MTH IMPVOL 102.5%MNY DF '], ['date.6','3MTH IMPVOL 105.0%MNY DF '], 
           ['date.7', '3MTH IMPVOL 110.0%MNY DF '],['date.8', '3MTH IMPVOL 120%MNY DF']]
    
    ivm_df = pd.DataFrame([])
    for col in cols:
        print(col)
        new = pd.read_excel(f"{rel_path}/Data/raw/fred/BB_IV.xlsx",sheet_name="data")[col]
        new.rename(columns = {col[0]:"date",col[1]:col[1].strip()},inplace=True)
        new = new[~new["date"].isna()].copy()
        new["date"] = pd.to_datetime(new["date"])
        new.set_index("date",inplace=True)   
        ivm_df = pd.concat([new,ivm_df],axis=1)
    
    ivm_df["diff"] =  ivm_df['3MTH IMPVOL 90.0%MNY DF'] - ivm_df['3MTH IMPVOL 102.5%MNY DF']
    ivm_df.reset_index(inplace=True)
    
            ### Swaptions
    cols = [['date', 'TYVIX1 INDEX'], ['date.1', 'TYVIX2 INDEX'],
            ['date.2','TYVIX3 INDEX'], ['date.3', 'USSN011 CURNCY'],
            ['date.4', 'USSN021 CURNCY'],['date.5', 'USSN031 CURNCY'],
            ['date.6', 'USSN041 CURNCY'], ['date.7','USSN051 CURNCY']]
    
    swaptions_df = pd.DataFrame([])
    for col in cols:
        print(col)
        new = pd.read_excel(f"{rel_path}/Data/raw/fred/swaption.xlsx",sheet_name="data")[col]
        new.rename(columns = {col[0]:"date",col[1]:col[1].strip()},inplace=True)
        new = new[~new["date"].isna()].copy()
        new["date"] = pd.to_datetime(new["date"])
        new.set_index("date",inplace=True)   
        swaptions_df = pd.concat([new,swaptions_df],axis=1)
    
    ivm_df["diff"] =  ivm_df['3MTH IMPVOL 90.0%MNY DF'] - ivm_df['3MTH IMPVOL 102.5%MNY DF']
    ivm_df.reset_index(inplace=True)
    
        ### VIX Indices
    cols = [['date', 'VIXZNP INDEX'], ['date.1', 'VIX1Y Index'], ['date.2',
           'VIX3M Index'], ['date.3', 'VIX6M Index'], ['date.4', 'VIXZBP INDEX'],
           ['date.5', 'VIXZFP INDEX'],['date.6', 'VIX INDEX'],['date.7', 'MOVE INDEX'],
           ['date.8', 'MOVE3M INDEX'], ['date.9', 'MOVE6M INDEX'],['date.10',
           'TYVIX INDEX']]
    
    # VIXZFP : 5yr Vol Index
    # VIXZNP : 10yr Vol Index
    # VIXZBP : 30yr Vol Index
    
    
    
    datavix = pd.DataFrame([])
    for col in cols:
        print(col)
        vix_df = pd.read_excel(f"{rel_path}/Data/raw/fred/BB_VIX.xlsx",sheet_name="data")[col]
        vix_df.rename(columns = {col[0]:"date"},inplace=True)
        vix_df = vix_df[~vix_df["date"].isna()].copy()
        vix_df["date"] = pd.to_datetime(vix_df["date"])
        vix_df.set_index("date",inplace=True)   
        datavix = pd.concat([vix_df,datavix],axis=1)
    datavix.reset_index(inplace=True)
    
        ### 10 yr constant treasury
    tsy10yr = pd.read_excel(f"{rel_path}/Data/raw/fred/DGS10.xls",skiprows=10)
    tsy10yr["DGS10"] = tsy10yr["DGS10"].replace(to_replace=0, method='ffill')
    effr = pd.read_excel(f"{rel_path}/Data/raw/fred/EFFR.xls",skiprows=10)
    effr["EFFR"] = effr["EFFR"].replace(to_replace=0, method='ffill')
    
    data_yield = tsy10yr.merge(effr,on="observation_date",how="outer")
    data_yield["dgs10ffr"] = data_yield["DGS10"] - data_yield["EFFR"]
    data_yield.rename(columns={"observation_date":"date"},inplace=True)
    
        ### Fed balance sheet
    data = pd.read_csv(f"{rel_path}/Data/raw/frb/FRB_H41_table1.csv",header=[0],skiprows=[1,2,3,4,5]).reset_index()
    data["date"] =  pd.to_datetime(data['Series Description'])
    data.drop(columns="index",inplace=True)
    
    colselect = ["date"] + [col for col in data.columns[1:] if re.search("Wednesday level",col)]
    vardict = dict(zip(data.columns[1:],[col.replace(": Wednesday level","") for col in data.columns[1:]]))
    
    data = data[colselect].copy().rename(columns=vardict)
    
    vardict = {'Liabilities and Capital: Other Factors Draining Reserve Balances: Currency in circulation':"Currency",
                'Liabilities and Capital: Other Factors Draining Reserve Balances: Treasury cash holdings':"Treasury cash holdings",
                'Liabilities and Capital: Liabilities: Reverse repurchase agreements':"Reverse repurchase agreements",
                'Liabilities and Capital: Other Factors Draining Reserve Balances: Other liabilities and capital':"Surplus",
                'Liabilities and Capital: Other Factors Draining Reserve Balances: Reserve balances with Federal Reserve Banks':"Reserve balances",
                'Liabilities and Capital: Liabilities: Deposits with F.R. Banks, other than reserve balances: Term deposits held by depository institutions':"Term deposits held by depository institutions",
                'Liabilities and Capital: Liabilities: Deposits with F.R. Banks, other than reserve balances: Foreign official':"Foreign official deposits",
                'Liabilities and Capital: Liabilities: Deposits: Other':"Other deposits",
                'Liabilities and Capital: Liabilities: Deposits with F.R. Banks, other than reserve balances: U.S. Treasury, General Account':'U.S. Treasury, General Account',
                'Liabilities and Capital: Other Factors Draining Reserve Balances: Treasury Contribution to Credit Facilities (Effective 2020-05-07)':"Treasury Contribution to Credit Facilities",
                'Assets: Securities Held Outright: U.S. Treasury securities':'U.S. Treasury securities',
                'Assets: Securities Held Outright: Federal agency debt securities':'Federal agency debt securities',
                'Assets: Securities Held Outright: Mortgage-backed securities':'Mortgage-backed securities',
                'Assets: Unamortized discounts on securities held outright':"Discounts",
                'Assets: Unamortized premiums on securities held outright':"Premiums",
                'Assets: Other: Repurchase agreements':'Repurchase agreements',
                'Assets: Liquidity and Credit Facilities: Loans: Money Market Mutual Fund Liquidity Facility (Post 2020-03-18)':"MMF",
                'Assets: Liquidity and Credit Facilities: Loans: Other credit extensions':'Other credit extensions',
                'Assets: Liquidity and Credit Facilities: Loans: Primary dealer credit facility (Post 2020-03-17)':"PDCF",
                'Assets: Liquidity and Credit Facilities: Loans: Payroll Protection Program Liquidity Facility':"PPPF",
                'Assets: Liquidity and Credit Facilities: Loans: Primary credit':'Primary credit',
                'Assets: Liquidity and Credit Facilities: Loans: Secondary credit':'Secondary credit',
                'Assets: Liquidity and Credit Facilities: Loans: Seasonal credit':'Seasonal credit',
                'Assets: Liquidity and Credit Facilities: Net portfolio holdings of Corporate Credit Facility LLC':"Corporate Credit Facility LLC",
                'Assets: Liquidity and Credit Facilities: Net portfolio holdings of Commercial Paper Funding Facility II LLC (Post 2020-04-14)':"Commercial Paper Funding Facility",
                'Assets: Liquidity and Credit Facilities: Net portfolio holdings of Municipal Liquidity Facility LLC (Effective 2020-05-26)':"Municipal Liquidity Facility",
                'Assets: Liquidity and Credit Facilities: Net portfolio holdings of MS Facilities LLC (Main Street Lending Program) (Effective 2020-06-01)':"MS Facilities LLC",
                'Assets: Liquidity and Credit Facilities: Net portfolio holdings of TALF II LLC (Effective 2020-06-16)':"TALF II",
                'Assets: Other Factors Supplying Reserve Balances: Float':'Float',
                'Assets: Central Bank Liquidity Swaps: Central bank liquidity swaps':"Central bank liquidity swaps",
                'Assets: Other Factors Supplying Reserve Balances: Other Federal Reserve assets':"Other Federal Reserve assets",
                'Assets: Other Factors Supplying Reserve Balances: Gold stock':"Gold stock",
                'Assets: Other Factors Supplying Reserve Balances: Treasury currency outstanding':"Treasury currency outstanding",
                'Assets: Other Factors Supplying Reserve Balances: Foreign currency denominated assets':"Foreign currency denominated assets",
                'Assets: Other: Special drawing rights certificate account':"SDR"}
    
    data = data[["date"]+list(vardict.keys())].copy().rename(columns=vardict)
    
        ### Do custom grouping
    definegrouping = [('date',1), ('Currency',1,"L"), ('Treasury cash holdings',7,"L"),
                      ("Term deposits held by depository institutions",7,"L"),
                      ("Foreign official deposits",7,"L"),
                      ("Treasury Contribution to Credit Facilities",7,"L"),
                      ("Other deposits",7,"L"),('U.S. Treasury, General Account',1,"L"),
                      ('Reverse repurchase agreements',1,"L"), ('Surplus',1,"L"),
                      ('Reserve balances',1,"L"), ('U.S. Treasury securities',1,"A"),
                      ('Federal agency debt securities',1,"A"), ('Mortgage-backed securities',1,"A"),
                      ('Discounts',2,"A"), ('Premiums',2,"A"), ('Repurchase agreements',1,"A"),
                      ('MMF',5,"A"), ('Other credit extensions',4,"A"), ('PDCF',5,"A"), ('PPPF',5,"A"), ('TALF II',5,"A"),
                      ('Primary credit',4,"A"), ('Secondary credit',4,"A"), ('Seasonal credit',4,"A"), 
                      ('Corporate Credit Facility LLC',6,"A"), ('Commercial Paper Funding Facility',6,"A"), 
                      ('Municipal Liquidity Facility',6,"A"), ('MS Facilities LLC',6,"A"),  ('Float',3,"A"), 
                      ('Central bank liquidity swaps',5,"A"), ('Other Federal Reserve assets',3,"A") ,
                      ('Gold stock',3,"A"), ('Treasury currency outstanding',3,"A"), 
                      ('Foreign currency denominated assets',3,"A"), ('SDR',3,"A")]
    
    groupdict = {2:"Sec. Discounts and Premiumns",3:"Other assets",
                 4: "Temp. credit fin. inst.",5:"Liquidity facility",
                 6:"Credit facility",7:"Other liabilities"}
    
    data_grouped=pd.DataFrame([])
    processeditem = []
    assetlist =[]
    liablist =[]
    
    for item in definegrouping:
        if item[1] == 1:
            data_grouped[item[0]] = data[item[0]].copy()
            if item[0] !="date":
                if item[2] =="A":
                    assetlist.append(item[0])
                else:
                    liablist.append(item[0])
    
        else:
            newitem = item[1]
            if item[0] in processeditem:
                continue
            else:
                itemlist =[]
                for itemb in definegrouping:
                    if newitem == itemb[1]:
                        itemlist.append(itemb[0])
                        processeditem.append(itemb[0])
                
            data_grouped[groupdict[item[1]]] = data[itemlist].sum(axis=1)
            if item[2] =="A":
                assetlist.append(groupdict[item[1]])
            else:
                liablist.append(groupdict[item[1]])
            
            
    # =============================================================================
    # pp = pprint.PrettyPrinter(width=41, compact=True)
    # pp.pprint(assetlist)     
    # data_grouped[assetlist].sum(axis=1)
    # pp.pprint(liablist)     
    # data_grouped[liablist].sum(axis=1)
    # 
    # =============================================================================
    data_grouped['d1_tsy'] =  data_grouped['U.S. Treasury securities'] - data_grouped['U.S. Treasury securities'].shift(1)
    data_grouped['d1_mbs'] =  data_grouped['Mortgage-backed securities'] - data_grouped['Mortgage-backed securities'].shift(1)
    data_grouped['d1_agency'] =  data_grouped['Federal agency debt securities'] - data_grouped['Federal agency debt securities'].shift(1)
     
    
    return meetingdates,qe_dic,ivm_df,datavix,data_yield,data_grouped,swaptions_df
    


def vis_data():
    datavix['scale_MOVEINDEX'] = datavix['MOVE INDEX'] / 3
    
    
    
    fig, ax = plt.subplots(1,figsize=(12,7))
    fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
    ivm_df.plot(x = "date", y = ['3MTH IMPVOL 90.0%MNY DF','3MTH IMPVOL 102.5%MNY DF'],ax=ax)
    fortmatstring = "{:.1f}"
    ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
    ax.grid(linestyle=':')
    
    fig, ax = plt.subplots(1,figsize=(12,7))
    fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
    ivm_df.plot(x = "date", y = "diff",ax=ax)
    fortmatstring = "{:.1f}"
    ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
    ax.grid(linestyle=':')
    
    
    fig, ax = plt.subplots(1,figsize=(12,7))
    fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
    fortmatstring = "{:.1f}"
    datavix.plot(x ="date", y=  "VIX INDEX",ax=ax,c="red",alpha=.6) 
    datavix.plot(x ="date", y=  "VIX1Y Index",ax=ax,c="purple",alpha=.6)
    datavix.plot(x ="date", y=  "VIXZNP INDEX",ax=ax,c="blue",alpha=.6)
    ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
    ax.grid(linestyle=':')
    
    fig, ax = plt.subplots(1,figsize=(12,7))
    fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
    fortmatstring = "{:.1f}"
    datavix.plot(x ="date", y=  'VIXZBP INDEX',ax=ax,c="red",alpha=.6) 
    datavix.plot(x ="date", y=  'VIXZFP INDEX',ax=ax,c="purple",alpha=.6)
    datavix.plot(x ="date", y=  "VIXZNP INDEX",ax=ax,c="blue",alpha=.6)
    ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
    ax.grid(linestyle=':')
    
    fig, ax = plt.subplots(1,figsize=(12,7))
    fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
    fortmatstring = "{:.1f}"
    datavix.plot(x ="date", y=  'MOVE INDEX',ax=ax,c="red",alpha=.6) 
    datavix.plot(x ="date", y=  'MOVE3M INDEX',ax=ax,c="purple",alpha=.6)
    datavix.plot(x ="date", y=  'MOVE6M INDEX',ax=ax,c="blue",alpha=.6)
    ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
    ax.grid(linestyle=':')
    
    fig, ax = plt.subplots(1,figsize=(12,7))
    fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
    fortmatstring = "{:.1f}"
    datavix.plot(x ="date", y=  'scale_MOVEINDEX',ax=ax,c="red",alpha=.6) 
    datavix.plot(x ="date", y=  'TYVIX INDEX',ax=ax,c="purple",alpha=.6)
    ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
    ax.grid(linestyle=':')
    
    
    
    
    startdate = "2008-01-01"
    enddate = "2016-01-01"
    
    fig, ax = plt.subplots(1,figsize=(12,7))
    fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
    #newdata[(newdata["date"]>=startdate) & (newdata["date"]<=enddate)].plot(x ="date", y=  "d1_tsy",ax=ax,c="blue",alpha=.6) 
    data_yield[(data_yield["date"]>=startdate) & (data_yield["date"]<=enddate)].plot(x ="date", y=  "dgs10ffr",ax=ax,label="10y-ffr Spread (left-axis)")
    fortmatstring = "{:.1f}"
    ax1 = ax.twinx()
    #datavix[(datavix["date"]>=startdate) & (datavix["date"]<=enddate)].plot(x ="date", y=  "VIX INDEX",c="red",alpha=.6,ax=ax1) 
    datavix[(datavix["date"]>=startdate) & (datavix["date"]<=enddate)].plot(x ="date", y=  "VIX1Y Index",c="red",alpha=.6,ax=ax1,label="VIX1Y Index (right-axis)")
    datavix[(datavix["date"]>=startdate) & (datavix["date"]<=enddate)].plot(x ="date", y=  'scale_MOVEINDEX',c="green",alpha=.6,ax=ax1,label="MOVE Index (right-axis)")
    for qedate in list(qe_dic.values()):
        plt.axvline(qedate,c="purple")
    ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
    ax.grid(linestyle=':')
    # added these three lines
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax1.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc=0)
    
    
    
    
    startdate = "2008-01-01"
    enddate = "2016-01-01"
    
    fig, ax = plt.subplots(1,figsize=(12,7))
    fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
    data_yield.plot(x ="date", y=  "dgs10ffr",ax=ax) 
    fortmatstring = "{:.1f}"
    ax1 = ax.twinx()
    data_grouped[(data_grouped["date"]>=startdate) & (data_grouped["date"]<=enddate)].plot(x = "date", y=  "d1_tsy",ax=ax1,c="red",alpha=.6) 
    #newdata[(newdata["date"]>=startdate) & (newdata["date"]<=enddate)].plot(x = "date", y=  "d1_tsy",ax=ax1,c="red",alpha=.6) 
    #datavix.plot(x ="date", y=  "VIX INDEX",ax=ax1,c="purple",alpha=.6) 
    datavix[(datavix["date"]>=startdate) & (datavix["date"]<=enddate)].plot(x = "date", y=  'scale_MOVEINDEX',ax=ax1,c="blue",alpha=.6) 
    # =============================================================================
    # for day in meetingdates:
    #     plt.axvline(day)
    # =============================================================================
    for qedate in list(qe_dic.values()):
        plt.axvline(qedate,c="purple")
    ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
    ax.grid(linestyle=':')
    
    
    
    
    startdate = "2020-06-01"
    enddate = "2022-01-01"
    
    fig, ax = plt.subplots(1,figsize=(12,7))
    fig.tight_layout(rect=[0.05, 0.05, 1, 0.95])
    #newdata[(newdata["date"]>=startdate) & (newdata["date"]<=enddate)].plot(x ="date", y=  "d1_tsy",ax=ax,c="blue",alpha=.6) 
    data_grouped[(data_grouped["date"]>=startdate) & (data_grouped["date"]<=enddate)].plot(x = "date", y=  "d1_tsy",ax=ax,c="red",alpha=.6) 
    fortmatstring = "{:.1f}"
    ax1 = ax.twinx()
    data_yield[(data_yield["date"]>=startdate) & (data_yield["date"]<=enddate)].plot(x ="date", y=  "dgs10ffr",ax=ax1,c="blue") 
    
    
    
    #datavix[(datavix["date"]>=startdate) & (datavix["date"]<=enddate)].plot(x ="date", y=  "VIX INDEX",c="red",alpha=.6,ax=ax1) 
    datavix[(datavix["date"]>=startdate) & (datavix["date"]<=enddate)].plot(x ="date", y=  "VIX1Y Index",c="red",alpha=.6,ax=ax1,label="VIX1Y Index (right-axis)")
    datavix[(datavix["date"]>=startdate) & (datavix["date"]<=enddate)].plot(x ="date", y=  'scale_MOVEINDEX',c="green",alpha=.6,ax=ax1,label="MOVE Index (right-axis)")
    for qedate in list(qe_dic.values()):
        plt.axvline(qedate,c="purple")
    ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x,p: fortmatstring.format(x)))
    ax.grid(linestyle=':')
    
    
    
    
    
    
    #ax.set_ylim(ymin ,ymax)
    #ax.set_ylabel(ylabel,fontsize=16)
    
    
    
    item = 'USRECM'
    recessions = fred.get_series(item, observation_start=start_date , observation_end=end_date)
    
    title  = info.title
    figname = "fig_treasury10yrffr"
    x = data["date"]
    y = data[info.title]
    ymax =data[info.title].max()*1.2
    ymin =min(0,data[info.title].min()*1.2)
    
    ylabel = info.units
    
    
    #plt.savefig(f"{path}/{figname}.pdf")
    
    ax1 = ax.twinx()
    
    ax1.fill_between(recessions.index,recessions,alpha=.2, color='grey')
    ax1.axis("off")
    
    #plt.savefig(f"{path}/{figname}.pdf")
    
    
    # =============================================================================
    
    
        ### FED Money Supply ###
    
    # in bn USD
    data = pd.read_csv(f"{rel_path}/Data/raw/frb/FRB_H6.csv",header=[0],skiprows=[1,2,3,4,5]).reset_index()
    data["month"] = data["Series Description"].apply(lambda x : str(x[-2:]))
    data["year"] = data["Series Description"].apply(lambda x : str(x[:4]))
    data["day"] = 1
    data["date"] =  pd.to_datetime(data[['year', 'month',"day"]])
    
    # Work with not seasonnally adjusted series for now.
    cols = ['date'] + [col for col in  data.columns if re.search("Not seasonally adjusted",col)]
    data = data[cols].copy()
     
    
    title = "M2"
    fig, ax = plt.subplots(1,figsize=(12,7))
    fig.tight_layout(rect=[0.05, 0.15, 1, 0.95])
    #fig.text(0.03 , 0.03,f"Source: {source}", horizontalalignment='left', verticalalignment='center', transform = ax.transAxes)
    #plt.gcf().subplots_adjust(left=0.05)
    fig.suptitle(title,fontsize=20)
    data['logM2'] = data['M2; Not seasonally adjusted'].apply(lambda x : np.log(x))
    data[data['date']>"1970-01-01"].plot.scatter('date','logM2',ax=ax)
    ax.legend(loc='upper left')
    ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x, p: "{:,.0f}".format(x)))
    ax.grid(linestyle=':')
    
    
    # =============================================================================
    
    # in bn USD
    
    
    for ass in assetlist:
        data_grouped[ass] = data_grouped[ass].apply(lambda x: x/1000)        
    
    for liab in liablist:
        data_grouped[liab] = data_grouped[liab].apply(lambda x: -x/1000)  
    
    title = "Fed Balance Sheet"
    fig, ax = plt.subplots(1,figsize=(12,7))
    fig.tight_layout(rect=[0.05, 0.15, 1, 0.95])
    fig.suptitle(title,fontsize=20)
    ylabel = "in bn USD"
    
    y = np.column_stack(data_grouped[assetlist].to_numpy())
    x = data_grouped['date'].to_numpy()
    ax.stackplot(x,y,labels=assetlist)
    
    y = np.column_stack(data_grouped[liablist].to_numpy())
    x = data_grouped['date'].to_numpy()
    ax.stackplot(x,y,labels=liablist)
    
    ax.legend(loc='upper left')
    ax.yaxis.set_major_formatter(tkr.FuncFormatter(lambda x, p: "{:,.0f}".format(x)))
    ax.grid(linestyle=':')
    ax.set_ylabel(ylabel,fontsize=16)
    
    
    
        ### Create Changes - H1/2020
    
    data_grouped.date.unique()
    for liab in liablist:
        data_grouped[liab] = data_grouped[liab].apply(lambda x: -x)  
    
    dataextract = data_grouped[(data_grouped["date"]=="2020-06-24") | (data_grouped["date"]=='2019-12-25')].copy()
    dataextract["date"] = dataextract["date"].dt.strftime('%Y-%m-%d')
    dataextract = dataextract.set_index("date")
    dataextract = dataextract.T.copy()
    dataextract["Change"] = dataextract['2020-06-24'] - dataextract['2019-12-25']
    dataextract["Change (in %)"] = dataextract["Change"] / dataextract['2019-12-25']
    print(dataextract)
    
    
    
        ### Treasury data
    
    data_treasury = pd.read_excel(f"{rel_path}/Data/raw/treasury_suplusdeficit.xls",nrows=479,header=0,converters= {'Receipts':str, 'Outlays':str, 'Deficit/Surplus (-)':str})
    
    data_treasury['Receipts'].apply(lambda x:x.replace("r","").replace(",",""))
    
    for col in ['Receipts', 'Outlays', 'Deficit/Surplus (-)']:
        data_treasury[col] = data_treasury[col].apply(lambda x:x.replace("r","").replace(",",""))
        data_treasury[col ] = data_treasury[col ].astype(float)
        
    newdata=pd.DataFrame([])
    newdata["date"]=pd.to_datetime(data_treasury["Period"])
    newdata["Netissuance"] = data_treasury['Borrowing from the Public'] 
    newdata["month"] = newdata["date"].dt.month
    newdata["year"] = newdata["date"].dt.year
    newdata["Netissuance"] = newdata["Netissuance"].apply(lambda x:x/1000)
    #newdata[newdata["date"]>="2010-01-01"].plot.line("date","Netissuance")
    
        
    dates = data_grouped['date'].groupby([data_grouped['date'].dt.year ,data_grouped['date'].dt.month]).max().to_numpy()
    
    monthly_treasuries =  data_grouped.loc[data_grouped["date"].isin(dates),["date",'U.S. Treasury securities']]
    monthly_treasuries["netpurchase"] = monthly_treasuries['U.S. Treasury securities'] - monthly_treasuries['U.S. Treasury securities'].shift(1)
    monthly_treasuries["month"] = monthly_treasuries["date"].dt.month
    monthly_treasuries["year"] = monthly_treasuries["date"].dt.year
        
    newdata = newdata.merge(monthly_treasuries,on=["month","year"],how="outer")
    newdata["changefreefloat"] = newdata["Netissuance"] - newdata["netpurchase"]
    
    fig, ax1 = plt.subplots(1,figsize=(12,7))
    newdata[newdata["date_x"]>="2018-01-01"].plot.line("date_x","changefreefloat",ax=ax1)
    newdata[newdata["date_x"]>="2018-01-01"].plot.line("date_x","Netissuance",ax=ax1)
    newdata[newdata["date_x"]>="2018-01-01"].plot.line("date_x","netpurchase",ax=ax1)
    #newdata[newdata["date_x"]>="2010-01-01"].plot.line("date_x","netpurchase",ax=ax)
    
    
        ### FOF - Treasury Security
    
       
    def import_data(path,startdate,datadict):
        data_hh = pd.read_csv(path,header=[0,1,2,3,4,5])
        data_hh = data_hh.loc[7:,:].copy()
        
        newcolname = ["period"] + [ col[5] for  col in list(data_hh.columns[1:])] 
        data_hh.columns = newcolname
        
        data_hh=data_hh.apply(pd.to_numeric, errors='ignore')
        data_hh["year"] = data_hh["period"].apply(lambda x:int(x[0:4]))
        data_hh["month"] = data_hh["period"].apply(lambda x : int(x[-1])*3)
        data_hh["day"] =1
        
        
        data_hh["date"] =  pd.to_datetime(data_hh[['year', 'month',"day"]])
        data_hh = data_hh[data_hh["date"]>=startdate].copy()
        data_hh = data_hh.apply(pd.to_numeric, errors='ignore')
        data_hh["date"] =  pd.to_datetime(data_hh["date"])
            ###
        
        data_hh = data_hh[list(datadict.keys())].copy()
        
        for item in datadict.keys():
            data_hh[ item] = data_hh[item].apply(lambda x:x/1000)
            
        data_hh.rename(columns=datadict,inplace=True)
            
        return data_hh
    
    path = f"{rel_path}/Data/raw/frb/FRB_F210.csv"
    startdate = "01-01-1990"
    datadict = {'FA313161205.Q':'Marketable Treasury securities',
                'FA153061105.Q':'Household sector',
                'FA103061103.Q':'Nonfinancial corporate business',
                'FA113061003.Q':'Nonfinancial noncorporate business',
                'FA213061105.Q':'State and local governments',
                'FA713061103.Q':'Monetary authority',
                'FA763061100.Q':'U.S.-chartered depository institutions',
                'FA753061103.Q':'Foreign banking offices in U.S.',
                'FA743061103.Q':'Banks in U.S.-affiliated areas',
                "FA473061105.Q":'Credit unions',
                "FA513061105.Q":"Property-casualty insurance companies",
                "FA543061105.Q":"Life insurance companies",
                "FA573061105.Q":"Private pension funds",
                "FA343061105.Q":"Federal government retirement funds",
                "FA223061143.Q":"State and local govt. retirement funds",
                "FA633061105.Q":"Money market funds",
                "FA653061105.Q":"Mutual funds",
                "FA553061103.Q":"Closed-end funds",
                "FA563061103.Q":"Exchange-traded funds",
                "FA403061105.Q":"Government-sponsored enterprises",
                "FA673061103.Q":"ABS issuers",
                "FA663061105.Q":"Brokers and dealers",
                "FA733061103.Q":"Holding companies",
                "FA503061303.Q":"Other financial business",
                "FA263061105.Q":"Rest of the world"}
    
    data = import_data(path,startdate,datadict)
    
    
    
