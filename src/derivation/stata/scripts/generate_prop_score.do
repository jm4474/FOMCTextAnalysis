

cd "/Users/olivergiesecke/Dropbox/MPCounterfactual/src/derivation/stata/scripts"

import delimited using ../../python/output/matlab_file,clear

	* Clean date
gen statadate=date(date,"MDY",2020)
format statadate %td
gen date_m=mofd(statadate)
format date_m %tm
drop statadate date 

	* Adjusted target following Angrist, Jorda, and Kuersteiner (2017)
gen target_change_adj=target_change
replace target_change_adj = 0.5 if target_change > 0.5
replace target_change_adj = -0.5 if target_change < -0.5
replace target_change_adj = -0.25 if target_change == -.3125
replace target_change_adj = 0.25 if target_change == .3125
replace target_change_adj = 0 if target_change == .0625

preserve
keep target_change_adj 
sort target_change_adj 
duplicates drop target_change,force
gen ord_adj_tchange = _n
tempfile policy_menu
save `policy_menu'
restore 

merge m:1 target_change_adj using `policy_menu',nogen
sort date_m

	* Contemporaneous inflation 
sort date_m
gen inflation = lagged_infl[_n+1]
twoway ( line lagged_infl date_m)(line inflation date_m)

/*
	* Detrend inflation 
gen time=_n
reg inflation time
predict det_inlation,r
twoway (line inflation date_m)( line det_inlation date_m)
*/

	* Contemporaneous unemployment
gen unemployment = lagged_unemp[_n+1]
twoway line  unemployment date_m

	* Define the samples
gen d_sample1=0
gen d_sample2=0
replace d_sample1 =1 if monthly("07/1989","MY")<date_m & date_m <= monthly("07/2005","MY")
replace d_sample2 =1 if monthly("07/1989","MY")<date_m & date_m <= monthly("12/2008","MY")

	* Define the range of target rate changes for the estimation of the prop score

replace lagged_infl=lagged_infl/12
replace lagged_unemp=lagged_unemp
gen d_y2k=monthly("01/2000","MY")==date_m 
	* table 1, column (1)
oprobit ord_adj_tchange  lagged_unemp lagged_infl  scale d_y2k d_nineeleven d_month_1 d_month_2 d_month_3 d_month_4 d_month_5 d_month_6 d_month_7 d_month_8 d_month_9 d_month_10 d_month_11 if d_sample1==1 
margins if d_sample1==1 , dydx(lagged_unemp lagged_infl) 

sort date_m
gen l2_infl=lagged_infl[_n-1]
gen l2_unemp=lagged_unemp[_n-1]

	* table 1, column (4)
local c4_spec "market_exp lagged_infl l2_infl lagged_unemp l2_unemp target_change_last target_change_last_fomc lead_dfedtar d_meeting scale d_y2k d_nineeleven d_month_1 d_month_2 d_month_3 d_month_4 d_month_5 d_month_6 d_month_7 d_month_8 d_month_9 d_month_10 d_month_11 d_month_1_fomc d_month_2_fomc d_month_3_fomc d_month_4_fomc d_month_5_fomc d_month_6_fomc d_month_7_fomc d_month_8_fomc d_month_9_fomc d_month_10_fomc d_month_11_fomc d_month_12_fomc"	
	
oprobit ord_adj_tchange `c4_spec' if d_sample1==1 

margins if d_sample1==1 , dydx(market_exp lagged_infl l2_infl lagged_unemp l2_unemp target_change_last target_change_last_fomc d_meeting) 

predict yhat1-yhat5,pr
rename yhat1 yhat_m050
rename yhat2 yhat_m025
rename yhat3 yhat_0
rename yhat4 yhat_025
rename yhat5 yhat_050

	* remove observations with Pr < 0.025
foreach var of varlist yhat_*{
replace `var'=. if `var'<0.025
}
	* Create dummies for outcomes
tab target_change_adj, gen(d_policy)
rename d_policy1 d_policy_m050
rename d_policy2 d_policy_m025
rename d_policy3 d_policy_0
rename d_policy4 d_policy_025
rename d_policy5 d_policy_050

	* Weight construction
foreach element in _m050 _m025 _0 _025 _050{
gen delta`element' = d_policy`element' / yhat`element' - d_policy_0 / yhat_0
}

	* Orthogonalize the weight with respect to the conditioning set
foreach element in _m050 _m025 _0 _025 _050{
reg delta`element' `c4_spec'
predict delta_res`element',r
}
	
	* Create changes in the outcome for 24 month

foreach horizon of numlist 1/24{
gen indpro_g`horizon' = log(indpro[_n+`horizon']) - log(indpro[_n])
}

foreach horizon of numlist 1/24{
gen unemployment_g`horizon' = unemployment[_n+`horizon'] - unemployment[_n]
}

	* Create auxiliary variable
foreach element in _m050 _m025 _0 _025 _050{
	foreach horizon of numlist 1/24{
		gen delta`element'indpro_g`horizon' = indpro_g`horizon'*delta_res`element'
		gen delta`element'unemployment_g`horizon' = unemployment_g`horizon'*delta_res`element'
	}
}

	* Get estimates at different horizons
gen horizon=_n	

foreach var of varlist unemployment indpro{
	gen b_`var'_025=.
	gen se_`var'_025=.
	gen ciub_`var'_025=.
	gen cilb_`var'_025=.

	foreach horizon of numlist 1/24{
		reg  delta_025`var'_g`horizon' if d_sample1==1
		capture replace b_`var'_025=_b[_cons] * 100 if horizon==`horizon'
		capture replace se_`var'_025=_se[_cons] * 100 if horizon==`horizon'
		replace ciub_`var'_025= b_`var'_025 + 1.68 * se_`var'_025 if horizon==`horizon'
		replace cilb_`var'_025= b_`var'_025 - 1.68 * se_`var'_025 if horizon==`horizon'
	}
}


twoway scatter ciub_indpro_025 b_indpro_025 cilb_indpro_025 horizon if horizon<=24, ///
c( l l l) lpattern(dash solid dash) m(i oh i) title(".25 on IP") name("IP025",replace) ///
legend(off) ytitle("Change IP (in %)")

twoway scatter ciub_unemployment_025 b_unemployment_025 cilb_unemployment_025 horizon if horizon<=24, ///
c( l l l) lpattern(dash solid dash) m(i oh i) title(".25 on Unemployment") name("U025",replace) ///
legend(off) ytitle("Change Unemployment (in %)")
	

	
gen b_inpro_m025=.
gen se_inpro_m025=.
gen ciub_inpro_m025=.
gen cilb_inpro_m025=.

foreach horizon of numlist 1/24{
	reg  delta_m025indpro_g`horizon' if d_sample1==1
	capture replace b_inpro_m025=_b[_cons] * 100 if horizon==`horizon'
	capture replace se_inpro_m025=_se[_cons] * 100 if horizon==`horizon'
	replace ciub_inpro_m025= b_inpro_m025 + 1.68 * se_inpro_m025 if horizon==`horizon'
	replace cilb_inpro_m025= b_inpro_m025 - 1.68 * se_inpro_m025 if horizon==`horizon'
}
	
twoway scatter ciub_inpro_m025 b_inpro_m025 cilb_inpro_m025 horizon if horizon<=24, ///
c( l l l) lpattern(dash solid dash) m(i oh i) title("-.25 on IP") name("IPm025",replace) ///
legend(off) ytitle("Change IP (in %)") yline(0, lstyle(grid))
	
	
	
	
	
