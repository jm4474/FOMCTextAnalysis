#Author: Anand Chitale
#This script reads in the derived matlab file in order to produce files of controls
#And outcomes for an odered probit. Output should be read and operated on by the matlab
#do_ord_prob_25.m and do_ord_prob_etu.m scripts. 


import pandas as pd
def main():
	for controls in ["simple","full"]:
		for outcome in ["","_etu"]:
			for mode in ["_quarterly","_yearly",""]:
				produce_controls_file(controls,mode,outcome)

def produce_controls_file(controls,mode,outcome):
	df = pd.read_csv("../../matlab/data/final_data_file.csv")
	df['d_y2k'] = df["d_y2k"].fillna(0)
	s_df = df[df.d_sample1==1]

	month_dummies=[
		"d_month_1","d_month_2","d_month_3","d_month_4","d_month_5","d_month_6","d_month_7",
		"d_month_8","d_month_9","d_month_10","d_month_11"
	]
	if controls == "full":
		xes = ['l1_ld_inflation'+mode,'l1_diff_unemp'+mode,
				'l2_diff_unemp','lag_DFEDTAR','target_change_last','target_change_last_fomc',
				'd_meeting','scale','d_y2k','d_nineeleven']
	else:
		xes = ['l1_ld_inflation'+mode,"l1_diff_unemp"+mode]

	xes = xes + month_dummies
	if outcome == "":
		space = [-0.5,-0.25,0,.25,.5]
		
		s_df.target_change_adj = s_df.target_change_adj.\
			astype(float,errors="ignore")

		s_df = s_df[s_df.target_change_adj.isin(space)]	
		out_df = s_df[['target_change_adj']]
		
		menu_df = s_df[['d_menu_adj_m050', \
		'd_menu_adj_m025', 'd_menu_adj_0', 'd_menu_adj_025', \
		'd_menu_adj_050','d_menu_adj_dec','d_menu_adj_unc','d_menu_adj_inc']]
		
		menu_df.to_csv("../../matlab/data/{}_controls{}_ord_prob_p1_menu.csv".format(controls,mode),index=False)
		out_df.to_csv("../../matlab/data/{}_controls{}_ord_prob_p1_targets.csv".format(controls,mode),index=False)

	elif outcome == "_etu":
		space = [-1,0,1]

		s_df = s_df[s_df.etu_outcome.isin(space)]

		out_df = s_df[['etu_outcome']]
		menu_df = s_df[['d_menu_adj_m050', \
		'd_menu_adj_m025', 'd_menu_adj_0', 'd_menu_adj_025', \
		'd_menu_adj_050','d_menu_adj_dec','d_menu_adj_unc','d_menu_adj_inc']]

		menu_df.to_csv("../../matlab/data/{}_controls{}{}_ord_prob_p1_menu.csv".format(controls,outcome,mode),index=False)
		out_df.to_csv("../../matlab/data/{}_controls{}{}_ord_prob_p1_targets.csv".format(controls,outcome,mode),index=False)

	x_df = s_df[xes]
	x_df.to_csv("../../matlab/data/{}_controls{}{}_ord_prob_p1.csv".format(controls,outcome,mode),index=False)
	

	print(x_df.columns)
if __name__ == "__main__":
	main()