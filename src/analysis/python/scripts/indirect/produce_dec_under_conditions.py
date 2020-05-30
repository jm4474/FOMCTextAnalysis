#Charts target decisions over economic variables

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    #inf_and_unemp()
    #nrou()
    #ind_pro()
    #nt_and_ne()
    moving_average()
    #nt_and_ne_no()
def moving_average():
    
    for period in [5,10]:
        df = pd.read_csv("../output/final_data_file.csv")
        df['date'] = pd.to_datetime(df['date_m'])
        
        df['rolling_average_inflation'] = df['l1_ld_inflation_yearly'].rolling(window=period*12).mean()
        df['rolling_average_ind_pro'] = df['INDPRO_PC1'].rolling(window=period*12).mean()

        df['l1_ld_inflation_yearly'] = df['l1_ld_inflation_yearly']-df['rolling_average_inflation']
        df['lagged_ind_pro'] = df['INDPRO_PC1'].shift(1)
        s_df = df[ (df['d_meeting'] == 1)]

        s_df = s_df[s_df.d_greenspan==True]
        
        s_df['lagged_reduced_ind_pro'] = (s_df['lagged_ind_pro']-(s_df['lagged_ind_pro'].mean()))

        #print(s_df)
        additions = "{}_ma".format(period)
        
        produce_colored_outcome_and_nte_graph(s_df,additions)
        produce_outcome_graph(s_df,additions)
        produce_ne_nt_graphs(s_df,additions)
        #print(s_df['INDPRO_PC1'].mean())
        #print(s_df[['date_m','INDPRO_PC1','l1_ld_inflation_yearly','rolling_average_inflation','lagged_reduced_ind_pro']])
        s_df.to_csv("../output/conditions_outcomes/ind_pro_and_inflation_ne_nt_{}.csv".format(additions))
def produce_ne_nt_graphs(s_df,additions):
    fig = plt.figure()
    ax_1 = fig.add_subplot(111)
    
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
    #plt.show()
    #fig.savefig("../output/conditions_outcomes/ind_pro_and_inflation_ne_nt_{}.png".format(additions),dpi=600)
def produce_outcome_graph(s_df,additions):
    e_df = s_df[s_df.etu_outcome == -1]
    t_df = s_df[s_df.etu_outcome == 1]
    u_df = s_df[s_df.etu_outcome == 0]

    
    fig = plt.figure()
    ax_1 = fig.add_subplot(111)
    
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
    #plt.show()
    #fig.savefig("../output/conditions_outcomes/ind_pro_and_inflation_outcomes_{}.png".format(additions),dpi=600)
def produce_colored_outcome_and_nte_graph(s_df,additions):
    nt_df = s_df[s_df.d_menu_adj_inc!=1]
    nt_e_df = nt_df[nt_df.etu_outcome == -1]
    nt_t_df = nt_df[nt_df.etu_outcome == 1]
    nt_u_df = nt_df[nt_df.etu_outcome == 0]

    fig = plt.figure()
    ax_1 = fig.add_subplot(111)

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
    #plt.title("Outcome plotted by conditions and menu")
    #plt.show()
    #fig.savefig("../output/conditions_outcomes/ind_pro_and_inflation_ne_nt_{}.png".format(additions),dpi=600)
def inf_and_unemp():
    df = pd.read_csv("../output/final_data_file.csv")
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
    #plt.show()
def nrou():
    df = pd.read_csv("../output/final_data_file.csv")
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
    #plt.show()

def ind_pro():
    df = pd.read_csv("../output/final_data_file.csv")

    ind_pro_df = pd.read_csv("../data/ind_pro_yearly_perc_change.csv")
    
    df['date'] = pd.to_datetime(df.date_m)
    ind_pro_df['date'] = pd.to_datetime(ind_pro_df.DATE)
    df = pd.merge(df,ind_pro_df,on="date",how="left")

    fig = plt.figure()
    ax_1 = fig.add_subplot(111)
    s_df = df[ (df['d_meeting'] == 1)]
    s_df = s_df[(s_df.date>pd.to_datetime('08-1-1987'))&(s_df.date<pd.to_datetime('02-1-2006'))]
    s_df['lagged_reduced_ind_pro'] = (s_df['INDPRO_PC1']-s_df['INDPRO_PC1'].mean()).shift(1)

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
    #plt.show()
    fig.savefig("../output/conditions_outcomes/ind_pro_and_inflation_outcomes.png",
        loc='upper right', )

def nt_and_ne():
    df = pd.read_csv("../output/final_data_file.csv")


    ind_pro_df = pd.read_csv("../data/ind_pro_ch.csv")
    
    df['date'] = pd.to_datetime(df.date_m)
    ind_pro_df['date'] = pd.to_datetime(ind_pro_df.DATE)
    df = pd.merge(df,ind_pro_df,on="date",how="left")

    fig = plt.figure()
    ax_1 = fig.add_subplot(111)
    s_df = df[ (df['d_meeting'] == 1)]
    s_df = s_df[(s_df.date>=pd.to_datetime('08-1-1987'))&(s_df.date<pd.to_datetime('02-1-2006'))]
    s_df['lagged_reduced_ind_pro'] = (s_df['INDPRO_CH1']-s_df['INDPRO_CH1'].mean()).shift(1)

    s_df['l1_ld_inflation_yearly'] = s_df['l1_ld_inflation_yearly']-s_df['l1_ld_inflation_yearly'].mean()
    print(len(s_df))
    

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
    print(s_df)
    plt.xlabel("lagged industrial production")
    plt.ylabel("lagged inflation")
    plt.xlim((-10,10))
    plt.ylim((-3,3))
    plt.axhline()
    plt.axvline()
    plt.legend()
    plt.title("Outcome plotted by conditions and menu")
    #plt.show()
    fig.savefig("../output/conditions_outcomes/ind_pro_and_inflation_ne_nt.png",dpi=600)


def nt_and_ne_no():
    df = pd.read_csv("../output/final_data_file.csv")


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
    #plt.show()
    fig.savefig("../output/conditions_outcomes/ind_pro_and_inflation_ne_nt.png")

if __name__ == "__main__":
    main()
