#Charts target decisions over economic variables

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    ind_pro()
    #plain()
    #nrou()
def plain():
    df = pd.read_csv("../../matlab/data/matlab_file.csv")
    fig = plt.figure()
    ax_1 = fig.add_subplot(111)
    s_df = df[ (df['d_meeting'] == 1)]
    et_df = s_df[s_df.etu_outcome!=0]
    e_df = s_df[s_df.etu_outcome == -1]
    t_df = s_df[s_df.etu_outcome == 1]
    u_df = s_df[s_df.etu_outcome == 0]

    ax_1.scatter(x=e_df["lagged_unemp"], y=e_df['l1_ld_inflation_yearly'],
                 c="red", label="ease",alpha=0.5)
    
    ax_1.scatter(x=u_df["lagged_unemp"],y=u_df['l1_ld_inflation_yearly'],c="blue")
    ax_1.scatter(x=t_df["lagged_unemp"], y=t_df['l1_ld_inflation_yearly'],
                 c="green", label="tighten")
    
    for i, txt in enumerate(pd.to_datetime(et_df.date_m).dt.year):
	    ax_1.annotate(\
	        txt, (et_df.lagged_unemp.iat[i], et_df.l1_ld_inflation_yearly.iat[i]))

    plt.xlabel("lagged unemployment")
    plt.ylabel("lagged inflation")
    plt.legend()
    plt.show()
def nrou():
    df = pd.read_csv("../../matlab/data/matlab_file.csv")
    nrou_df = pd.read_csv("../data/NROU.csv")
    
    df['date'] = pd.to_datetime(df.date_m)
    nrou_df['date'] = pd.to_datetime(nrou_df.DATE)
    df = pd.merge(df,nrou_df,on="date",how="left")
    df['l1_unemp_nrou'] = df['NROU'].shift(1)
    fig = plt.figure()
    ax_1 = fig.add_subplot(111)
    s_df = df[ (df['d_sample1']==1)&(df['d_meeting'] == 1)]
    
    et_df = s_df[s_df.etu_outcome!=0]

    e_df = s_df[s_df.etu_outcome == -1]
    t_df = s_df[s_df.etu_outcome == 1]
    u_df = s_df[s_df.etu_outcome == 0]

    ax_1.scatter(x=e_df["l1_unemp_nrou"], y=e_df['l1_ld_inflation_yearly'],
    	c="red", label="ease")
    
    ax_1.scatter(x=u_df["l1_unemp_nrou"],y=u_df['l1_ld_inflation_yearly'],
    	c="blue",label="unchanged")
    ax_1.scatter(x=t_df["l1_unemp_nrou"], y=t_df['l1_ld_inflation_yearly'],
    	c="green", label="tighten")
    
    for i, txt in enumerate(pd.to_datetime(et_df.date_m).dt.year):
	    ax_1.annotate(\
	        txt, (et_df.l1_unemp_nrou.iat[i], et_df.l1_ld_inflation_yearly.iat[i]))

    plt.xlabel("lagged unemployment")
    plt.ylabel("lagged inflation")
    plt.legend()
    plt.show()

def ind_pro():
    df = pd.read_csv("../../matlab/data/matlab_file.csv")


    ind_pro_df = pd.read_csv("../data/ind_pro_ch.csv")
    
    df['date'] = pd.to_datetime(df.date_m)
    ind_pro_df['date'] = pd.to_datetime(ind_pro_df.DATE)
    df = pd.merge(df,ind_pro_df,on="date",how="left")
    df['lagged_reduced_ind_pro'] = (df['INDPRO_CH1']-df['INDPRO_CH1'].mean()).shift(1)
    fig = plt.figure()
    ax_1 = fig.add_subplot(111)
    s_df = df[ (df['d_meeting'] == 1)]
    #print(s_df['lagged_reduced_ind_pro'])
    et_df = s_df[s_df.etu_outcome!=0]
    e_df = s_df[s_df.etu_outcome == -1]
    t_df = s_df[s_df.etu_outcome == 1]
    u_df = s_df[s_df.etu_outcome == 0]


    ax_1.scatter(e_df['lagged_reduced_ind_pro'], y=e_df['l1_ld_inflation_yearly'],
                 c="red", label="ease",alpha=0.5)
    
    ax_1.scatter(x=u_df["lagged_reduced_ind_pro"],y=u_df['l1_ld_inflation_yearly'],c="blue")
    ax_1.scatter(x=t_df["lagged_reduced_ind_pro"], y=t_df['l1_ld_inflation_yearly'],
                 c="green", label="tighten")
    
    for i, txt in enumerate(pd.to_datetime(et_df.date_m).dt.year):
        ax_1.annotate(\
            txt, (et_df.lagged_reduced_ind_pro.iat[i], et_df.l1_ld_inflation_yearly.iat[i]))

    plt.xlabel("lagged ind_pro")
    plt.ylabel("lagged inflation")
    plt.legend()
    plt.show()
if __name__ == "__main__":
    main()
