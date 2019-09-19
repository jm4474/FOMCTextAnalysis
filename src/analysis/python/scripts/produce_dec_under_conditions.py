#Charts target decisions over economic variables

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    #inf_and_unemp()
    #nrou()
    ind_pro()
    #nt_and_ne()
    #moving_average()
    nt_and_ne_no()
def inf_and_unemp():
    df = pd.read_csv("../../matlab/data/matlab_file.csv")
    fig = plt.figure()
    ax_1 = fig.add_subplot(111)
    s_df = df[ (df['d_meeting'] == 1)]

    et_df = s_df[s_df.etu_outcome!=0]
    e_df = s_df[s_df.etu_outcome == -1]
    t_df = s_df[s_df.etu_outcome == 1]
    u_df = s_df[s_df.etu_outcome == 0]

    ax_1.scatter(x=e_df["lagged_unemp"], y=e_df['l1_ld_inflation_yearly'],
                 c="red", label="ease")
    
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

    fig = plt.figure()
    ax_1 = fig.add_subplot(111)
    s_df = df[ (df['d_meeting'] == 1)]
    s_df = s_df[(s_df.date>pd.to_datetime('08-1-1987'))&(s_df.date<pd.to_datetime('02-1-2006'))]
    s_df['lagged_reduced_ind_pro'] = (s_df['INDPRO_CH1']-s_df['INDPRO_CH1'].mean()).shift(1)

    s_df['l1_ld_inflation_yearly'] = s_df['l1_ld_inflation_yearly']-s_df['l1_ld_inflation_yearly'].mean()

    #print(s_df['lagged_reduced_ind_pro'])
    e_df = s_df[s_df.etu_outcome == -1]
    t_df = s_df[s_df.etu_outcome == 1]
    u_df = s_df[s_df.etu_outcome == 0]

    

    
    ax_1.plot(u_df["lagged_reduced_ind_pro"],u_df['l1_ld_inflation_yearly'],
                "ok", label="unchanged",fillstyle="none",
                )
    ax_1.plot(t_df["lagged_reduced_ind_pro"], t_df['l1_ld_inflation_yearly'],
                "^k", label="tighten",fillstyle="none",
                )

    ax_1.plot(e_df['lagged_reduced_ind_pro'], e_df['l1_ld_inflation_yearly'],
                "vk",  label="ease", fillstyle="none",
                )

    
    for i, txt in enumerate(pd.to_datetime(s_df.date_m).dt.year):
        ax_1.annotate(\
            txt, (s_df.lagged_reduced_ind_pro.iat[i], s_df.l1_ld_inflation_yearly.iat[i]))

    plt.xlabel("lagged industrial production")
    plt.ylabel("lagged inflation")
    plt.xlim((-10,10))
    plt.ylim((-3,3))
    plt.axhline()
    plt.axvline()
    plt.legend()
    plt.title("Outcomes plotted by inflation and industrial production")
    plt.show()
    fig.savefig("../output/conditions_outcomes/ind_pro_and_inflation_outcomes.png",
        loc='upper right', )

def nt_and_ne():
    df = pd.read_csv("../../matlab/data/matlab_file.csv")


    ind_pro_df = pd.read_csv("../data/ind_pro_ch.csv")
    
    df['date'] = pd.to_datetime(df.date_m)
    ind_pro_df['date'] = pd.to_datetime(ind_pro_df.DATE)
    df = pd.merge(df,ind_pro_df,on="date",how="left")

    fig = plt.figure()
    ax_1 = fig.add_subplot(111)
    s_df = df[ (df['d_meeting'] == 1)]
    s_df = s_df[(s_df.date>pd.to_datetime('08-1-1987'))&(s_df.date<pd.to_datetime('02-1-2006'))]
    s_df['lagged_reduced_ind_pro'] = (s_df['INDPRO_CH1']-s_df['INDPRO_CH1'].mean()).shift(1)

    s_df['l1_ld_inflation_yearly'] = s_df['l1_ld_inflation_yearly']-s_df['l1_ld_inflation_yearly'].mean()

    #print(s_df['lagged_reduced_ind_pro'])
    #print(s_df[(s_df.d_menu_adj_inc==0)&(s_df.d_menu_adj_dec==0)])
    #print(s_df[[x for x in s_df.columns if "d_menu_adj" in x]])
    

    nt_df = s_df[s_df.d_menu_adj_inc!=1]
    nt_e_df = nt_df[nt_df.etu_outcome == -1]
    nt_t_df = nt_df[nt_df.etu_outcome == 1]
    nt_u_df = nt_df[nt_df.etu_outcome == 0]

    
    ne_df = s_df[s_df.d_menu_adj_dec!=1]
    ne_e_df = ne_df[ne_df.etu_outcome == -1]
    ne_t_df = ne_df[ne_df.etu_outcome == 1]
    ne_u_df = ne_df[ne_df.etu_outcome == 0]


    #Circles for no tightening option
    ax_1.scatter(x=nt_e_df['lagged_reduced_ind_pro'], y=nt_e_df['l1_ld_inflation_yearly'],
                 c="red", label="no_tightening_in_menu_outcome_easing",marker='o')
    
    ax_1.scatter(x=nt_u_df["lagged_reduced_ind_pro"],y=nt_u_df['l1_ld_inflation_yearly'],
        c="blue",label="no_tightening_in_menu_outcome_unchanged",marker='o')
    
    ax_1.scatter(x=nt_t_df["lagged_reduced_ind_pro"], y=nt_t_df['l1_ld_inflation_yearly'],
                 c="green", label="no_tightening_in_menu_outcome_tightening",marker='o')

    #Squares for no easing option
    ax_1.scatter(x=ne_e_df['lagged_reduced_ind_pro'], y=ne_e_df['l1_ld_inflation_yearly'],
                 c="red", label="no_easing_in_menu_outcome_easing",marker='s')
    
    ax_1.scatter(x=ne_u_df["lagged_reduced_ind_pro"],y=ne_u_df['l1_ld_inflation_yearly'],
        c="blue",label="no_easing_in_menu_outcome_unchanged",marker='s')
    
    ax_1.scatter(x=ne_t_df["lagged_reduced_ind_pro"], y=ne_t_df['l1_ld_inflation_yearly'],
                 c="green", label="no_easing_in_menu_outcome_tighten",marker='s')
    
    for i, txt in enumerate(pd.to_datetime(nt_df.date_m).dt.year):
        ax_1.annotate(\
            txt, (nt_df.lagged_reduced_ind_pro.iat[i], nt_df.l1_ld_inflation_yearly.iat[i]))
    for i, txt in enumerate(pd.to_datetime(ne_df.date_m).dt.year):
        ax_1.annotate(\
            txt, (ne_df.lagged_reduced_ind_pro.iat[i], ne_df.l1_ld_inflation_yearly.iat[i]))

    plt.xlabel("lagged industrial production")
    plt.ylabel("lagged inflation")
    plt.xlim((-10,10))
    plt.ylim((-3,3))
    plt.axhline()
    plt.axvline()
    plt.legend()
    plt.title("Outcome plotted by conditions and menu")
    plt.show()
    fig.savefig("../output/conditions_outcomes/ind_pro_and_inflation_ne_nt.png")

def moving_average():
    for period in [5,10,15,20]:
        df = pd.read_csv("../../matlab/data/matlab_file.csv")


        ind_pro_df = pd.read_csv("../data/ind_pro_ch.csv")
        
        df['date'] = pd.to_datetime(df.date_m)
        ind_pro_df['date'] = pd.to_datetime(ind_pro_df.DATE)
        df = pd.merge(df,ind_pro_df,on="date",how="left")

        fig = plt.figure()
        ax_1 = fig.add_subplot(111)
        s_df = df[ (df['d_meeting'] == 1)]
        s_df = s_df[(s_df.date>pd.to_datetime('08-1-1987'))&(s_df.date<pd.to_datetime('02-1-2006'))]
        
        s_df['5_year_period'] = s_df.reset_index().index//period

        means = s_df.groupby('5_year_period')['INDPRO_CH1'].mean().reset_index().rename(columns={"INDPRO_CH1":"m_average"})
        
        
        s_df = s_df.merge(means,on="5_year_period")
        s_df['lagged_reduced_ind_pro'] = (s_df['INDPRO_CH1']-s_df['m_average']).shift(1)
        print(s_df['m_average'])
        print(s_df[['INDPRO_CH1','lagged_reduced_ind_pro']])
        s_df['l1_ld_inflation_yearly'] = s_df['l1_ld_inflation_yearly']-s_df['l1_ld_inflation_yearly'].mean()

        #print(s_df['lagged_reduced_ind_pro'])
        #print(s_df[(s_df.d_menu_adj_inc==0)&(s_df.d_menu_adj_dec==0)])
        #print(s_df[[x for x in s_df.columns if "d_menu_adj" in x]])
        

        nt_df = s_df[s_df.d_menu_adj_inc!=1]
        nt_e_df = nt_df[nt_df.etu_outcome == -1]
        nt_t_df = nt_df[nt_df.etu_outcome == 1]
        nt_u_df = nt_df[nt_df.etu_outcome == 0]

        
        ne_df = s_df[s_df.d_menu_adj_dec!=1]
        ne_e_df = ne_df[ne_df.etu_outcome == -1]
        ne_t_df = ne_df[ne_df.etu_outcome == 1]
        ne_u_df = ne_df[ne_df.etu_outcome == 0]


        #Circles for no tightening option
        ax_1.scatter(x=nt_e_df['lagged_reduced_ind_pro'], y=nt_e_df['l1_ld_inflation_yearly'],
                     c="red", label="no_tightening_in_menu_outcome_easing",marker='o')
        
        ax_1.scatter(x=nt_u_df["lagged_reduced_ind_pro"],y=nt_u_df['l1_ld_inflation_yearly'],
            c="blue",label="no_tightening_in_menu_outcome_unchanged",marker='o')
        
        ax_1.scatter(x=nt_t_df["lagged_reduced_ind_pro"], y=nt_t_df['l1_ld_inflation_yearly'],
                     c="green", label="no_tightening_in_menu_outcome_tightening",marker='o')

        #Squares for no easing option
        ax_1.scatter(x=ne_e_df['lagged_reduced_ind_pro'], y=ne_e_df['l1_ld_inflation_yearly'],
                     c="red", label="no_easing_in_menu_outcome_easing",marker='s')
        
        ax_1.scatter(x=ne_u_df["lagged_reduced_ind_pro"],y=ne_u_df['l1_ld_inflation_yearly'],
            c="blue",label="no_easing_in_menu_outcome_unchanged",marker='s')
        
        ax_1.scatter(x=ne_t_df["lagged_reduced_ind_pro"], y=ne_t_df['l1_ld_inflation_yearly'],
                     c="green", label="no_easing_in_menu_outcome_tighten",marker='s')
        
        for i, txt in enumerate(pd.to_datetime(nt_df.date_m).dt.year):
            ax_1.annotate(\
                txt, (nt_df.lagged_reduced_ind_pro.iat[i], nt_df.l1_ld_inflation_yearly.iat[i]))
        for i, txt in enumerate(pd.to_datetime(ne_df.date_m).dt.year):
            ax_1.annotate(\
                txt, (ne_df.lagged_reduced_ind_pro.iat[i], ne_df.l1_ld_inflation_yearly.iat[i]))

        plt.xlabel("lagged ind_pro")
        plt.ylabel("lagged inflation")
        plt.xlim((-10,10))
        plt.ylim((-3,3))
        plt.axhline()
        plt.axvline()
        plt.legend()
        plt.title("Outcome plotted by conditions and menu")
        plt.show()
        fig.savefig("../output/conditions_outcomes/ind_pro_and_inflation_ne_nt_{}_year_m_a.png".format(period))
def nt_and_ne_no():
    df = pd.read_csv("../../matlab/data/matlab_file.csv")


    ind_pro_df = pd.read_csv("../data/ind_pro_ch.csv")
    
    df['date'] = pd.to_datetime(df.date_m)
    ind_pro_df['date'] = pd.to_datetime(ind_pro_df.DATE)
    df = pd.merge(df,ind_pro_df,on="date",how="left")

    fig = plt.figure()
    ax_1 = fig.add_subplot(111)
    s_df = df[ (df['d_meeting'] == 1)]
    s_df = s_df[(s_df.date>pd.to_datetime('08-1-1987'))&(s_df.date<pd.to_datetime('02-1-2006'))]
    s_df['lagged_reduced_ind_pro'] = (s_df['INDPRO_CH1']-s_df['INDPRO_CH1'].mean()).shift(1)

    s_df['l1_ld_inflation_yearly'] = s_df['l1_ld_inflation_yearly']-s_df['l1_ld_inflation_yearly'].mean()

    #print(s_df['lagged_reduced_ind_pro'])
    #print(s_df[(s_df.d_menu_adj_inc==0)&(s_df.d_menu_adj_dec==0)])
    #print(s_df[[x for x in s_df.columns if "d_menu_adj" in x]])
    

    nt_df = s_df[s_df.d_menu_adj_inc!=1]
    #nt_e_df = nt_df[nt_df.etu_outcome == -1]
    #nt_t_df = nt_df[nt_df.etu_outcome == 1]
    #nt_u_df = nt_df[nt_df.etu_outcome == 0]

    
    ne_df = s_df[s_df.d_menu_adj_dec!=1]
    #ne_e_df = ne_df[ne_df.etu_outcome == -1]
    #ne_t_df = ne_df[ne_df.etu_outcome == 1]
    #ne_u_df = ne_df[ne_df.etu_outcome == 0]


    #Circles for no tightening option
    ax_1.plot(nt_df['lagged_reduced_ind_pro'], nt_df['l1_ld_inflation_yearly'],
        'xk', label="no_tightening_in_menu",fillstyle="none")
    
    
    #Squares for no easing option
    ax_1.plot(ne_df["lagged_reduced_ind_pro"], ne_df['l1_ld_inflation_yearly'],
        'ok',label="no_easing_in_menu",fillstyle="none")
    
    for i, txt in enumerate(pd.to_datetime(nt_df.date_m).dt.year):
        ax_1.annotate(\
            txt, (nt_df.lagged_reduced_ind_pro.iat[i], nt_df.l1_ld_inflation_yearly.iat[i]))
    for i, txt in enumerate(pd.to_datetime(ne_df.date_m).dt.year):
        ax_1.annotate(\
            txt, (ne_df.lagged_reduced_ind_pro.iat[i], ne_df.l1_ld_inflation_yearly.iat[i]))

    plt.xlabel("lagged industrial production")
    plt.ylabel("lagged inflation")
    plt.xlim((-10,10))
    plt.ylim((-3,3))
    plt.axhline()
    plt.axvline()
    plt.legend()
    plt.title("Outcome plotted by conditions and menu")
    plt.show()
    fig.savefig("../output/conditions_outcomes/ind_pro_and_inflation_ne_nt.png")

if __name__ == "__main__":
    main()
