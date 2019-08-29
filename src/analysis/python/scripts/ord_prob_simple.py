import pandas as pd
def main():
	df = pd.read_csv("../../matlab/data/matlab_file.csv")
	#df['l1_unemp'] = df.unemp.shift(1)
	#df['l2_unemp'] = df.unemp.shift(2)
	df['d_y2k'] = df["d_y2k"].fillna(0)
	s_df = df[df.d_sample1==1]

	month_dummies=[
		"d_month_1","d_month_2","d_month_3","d_month_4","d_month_5","d_month_6","d_month_7",
		"d_month_8","d_month_9","d_month_10","d_month_11"
	]

	space = [-0.5,-0.25,0,.25,.5]
	first_test = ['l1_ld_inflation',"l1_diff_unemp"]
	#first_test.extend(month_dummies)

	s_df.target_change_adj = s_df.target_change_adj.\
		astype(float,errors="ignore")

	s_df = s_df[s_df.target_change_adj.isin(space)]
	s_df.to_csv("controls_view.csv")	
	print(first_test)
	#print(s_df[['date','l1_unemp','l1_inflation']])
	x_df = s_df[first_test]
	out_df = s_df[['target_change_adj']]
	print(len(s_df))
	#print(s_df)
	menu_df = s_df[['date_m','d_menu_adj_m050', \
		'd_menu_adj_m025', 'd_menu_adj_0', 'd_menu_adj_025', \
		'd_menu_adj_050']]
	menu_df.to_csv("../../matlab/data/simple_controls_ord_prob_p1_menu.csv",index=False)
	x_df.to_csv("../../matlab/data/simple_controls_ord_prob_p1.csv",index=False)
	out_df.to_csv("../../matlab/data/simple_controls_targets_ord_prob_p1.csv",index=False)

if __name__ == "__main__":
	main()