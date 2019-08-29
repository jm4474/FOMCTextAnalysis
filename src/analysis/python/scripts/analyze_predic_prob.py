import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
def main():
    modes = ["simple_controls","simple_controls_yearly","simple_controls_quarterly",
        "full_controls","full_controls_quarterly","full_controls_yearly"]
    for mode in modes:
        produce_graphs(mode,mode.split("controls")[-1])
def produce_graphs(mode,addition):
    prediction_names = ['m050', 'm025', '0', '025', '050']
    p_df = pd.read_csv("../../matlab/data/predicted_prob_{}.csv".format(mode), header=None,
                       names=prediction_names)
    m_df = pd.read_csv(
        "../../matlab/data/{}_ord_prob_p1_menu.csv".format(mode))
    d_df = pd.read_csv(
        "../../matlab/data/{}_targets_ord_prob_p1.csv".format(mode))
    x_df = pd.read_csv("../../matlab/data/{}_ord_prob_p1.csv".format(mode))
    merge_df = pd.merge(p_df, m_df, left_index=True, right_index=True)

    merge_df = merge_df.replace(0, np.nan).replace(False, np.nan)
    merge_df = pd.merge(merge_df, d_df, left_index=True, right_index=True)
    merge_df = pd.merge(merge_df, x_df, left_index=True, right_index=True)

    print(merge_df)
    print(merge_df.columns)

    graph_df = merge_df[['l1_ld_inflation'+addition, 'l1_diff_unemp'+addition,
                         'm050', 'm025', '0', '025', '050', 'd_menu_adj_m050', 'd_menu_adj_m025',
                         'd_menu_adj_0', 'd_menu_adj_025', 'd_menu_adj_050']]
    print(graph_df)

    min = graph_df[graph_df.columns[2:6]].min().min()
    max = graph_df[graph_df.columns[2:6]].max().max()
    for action in prediction_names:
        g_p_df = graph_df[[action, 'l1_ld_inflation'+addition,
                           'l1_diff_unemp'+addition, 'd_menu_adj_'+action]]
        in_menu = g_p_df[g_p_df["d_menu_adj_"+action] == 1]
        out_menu = g_p_df[g_p_df["d_menu_adj_"+action].isnull()]
        fig = plt.figure()
        ax_1 = fig.add_subplot(111)
        print(g_p_df)
        om_sc = ax_1.scatter(x=out_menu["l1_diff_unemp"+addition], y=out_menu["l1_ld_inflation"+addition],
                             c=out_menu[action], cmap="Reds", marker="s",vmin=min, vmax=max
                             ,s=50)
        im_sc = ax_1.scatter(x=in_menu["l1_diff_unemp"+addition], y=in_menu["l1_ld_inflation"+addition],
                             c=in_menu[action], cmap="Blues", marker="o", vmin=min, vmax=max
                             ,s=20)
        
        plt.colorbar(im_sc)
        plt.colorbar(om_sc)
        plt.title("{} {}".format(str(action),str(mode)))
        plt.xlabel("Unemployment")
        plt.ylabel("Inflation")

        plt.savefig("../output/probit_graphs/{}{}.png".format(str(mode),str(action)))


    # print(merge_df[['050','d_menu_050','target_change_adj']])
    # print(merge_df.count())
if __name__ == "__main__":
    main()
