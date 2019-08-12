cd "/Users/olivergiesecke/Dropbox/MPCounterfactual/src/analysis/stata/scripts/"

import delimited using ../../../analysis/python/output/news_text_expectations.csv,clear
gen statadate=date(date,"YMD",2020)
format statadate %td
gen date_m=mofd(statadate)
format date_m %tm
drop statadate date month year
tempfile news_surprise
save `news_surprise'

import delimited using ../../../derivation/python/output/matlab_file,clear
	* Clean date
gen statadate=date(date,"MDY",2020)
format statadate %td
gen date_m=mofd(statadate)
format date_m %tm
drop statadate date 
save ../data/master_data,replace


use ../../../collection/python/data/Fed_shocks.dta,clear
gen date_m=mofd(date)
format date_m %tm
twoway scatter d_fed_future_scaled date_m
collapse (sum) d_fed_future_scaled,by(date_m)
merge 1:1 date_m using `news_surprise'
drop _merge
merge 1:1 date_m using ../data/master_data, keepusing(market_exp)
sort date_m
replace d_fed_future_scaled = market_exp if d_fed_future_scaled == .
twoway scatter d_fed_future_scaled date_m
drop _merge market_exp
drop if date_m >= monthly("2008/01","YM")

gen d_indicator = (indicator=="True")

gen fed_future_scaled_abs=abs(d_fed_future_scaled )
twoway scatter d_indicator fed_future_scaled_abs 
twoway scatter score fed_future_scaled_abs 

*browse if d_indicator == 1 & fed_future_scaled_abs < 0.01


********************************************************************************
*** PREPROCESSING ***

use ../data/master_data,clear

	* Rename the policy dummies
foreach element in m075 m050 m025 0 025 050 075{
	rename d_`element' d_menu_`element'
}

foreach element in m075 m050 m025 0 025 050 075{
	gen d_menu_adj_`element' = d_menu_`element'
}

replace d_menu_adj_m050 = (d_menu_adj_m050 + d_menu_adj_m075) > 0
replace d_menu_adj_050 = (d_menu_adj_050 + d_menu_adj_075) > 0
drop d_menu_adj_m075 d_menu_adj_075

foreach element in dec unc inc{
	rename d_`element' d_menu_`element'
}

	* Define the samples
gen d_sample1=0
gen d_sample2=0
replace d_sample1 =1 if monthly("07/1989","MY")<date_m & date_m <= monthly("07/2005","MY")
replace d_sample2 =1 if monthly("07/1989","MY")<date_m & date_m <= monthly("12/2008","MY")

	* Adjusted target following Angrist, Jorda, and Kuersteiner (2017)
gen target_change_adj=target_change
replace target_change_adj = 0.5 if target_change > 0.5 // 4 months of adj.
replace target_change_adj = -0.5 if target_change < -0.5
replace target_change_adj = -0.25 if target_change == -.3125 // 1 month adj.

gen target_change_simple=target_change
replace target_change_simple = 1 if target_change > 0 // 4 months of adj.
replace target_change_simple = -1 if target_change < 0


	* Show overall sample stats
tab target_change if d_sample1 ==1 
// Sample size matches: 192 obs, 60 monthly changes
tab target_change if d_sample2 ==1
// Sample size matches: 232 obs, 75 monthly changes (3 changes acc.)

	* Add the discrete policy choice
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
	
	* Variable definition
gen d_y2k=monthly("01/2000","MY")==date_m 
sort date_m
gen l1_inflation = inflation[_n-1]
gen l2_inflation = inflation[_n-2]

gen l1_diff_unemp = lagged_unemp - lagged_unemp[_n-3]
gen l2_diff_unemp = l1_diff_unemp[_n-3]-l1_diff_unemp[_n-6]

gen l1_inf=(log(pcepi[_n-1])-log(pcepi[_n-4]))*100
gen l2_inf=(log(pcepi[_n-4])-log(pcepi[_n-7]))*100

gen l1_target_change = target_change[_n-1]
gen l2_target_change = target_change[_n-2]
gen l3_target_change = target_change[_n-3]
gen l4_target_change = target_change[_n-4]
gen l5_target_change = target_change[_n-5]
gen Fl1_target_change = l1_target_change * d_meeting

	* Label variables
label var d_menu_adj_m050 "Option -50bps"
label var d_menu_adj_m025 "Option -25bps"
label var d_menu_adj_0 "Option 0 bps"
label var d_menu_adj_025 "Option +25bps"
label var d_menu_adj_050 "Option +50bps"
label var market_exp "FFR Expectation"
label var l1_inf "Inflation, Lag 1"
label var l2_inf "Inflation, Lag 2"
label var l1_diff_unemp "Unemployment, Lag 1"
label var l2_diff_unemp "Unemployment, Lag 2"
label var lag_dfedtar "Target Rate, Lag 1"
label var l1_target_change "Last Change"
label var l2_target_change "Change, Lag 2"
label var l3_target_change "Change, Lag 3"
label var Fl1_target_change "FOMC $\times$ Last Change"
label var d_meeting "FOMC"
label var d_menu_dec "Option Expansion"
label var d_menu_unc "Option No Change"
label var d_menu_inc "Option Tightening"

	* Create dummies for outcomes
gen d_policy_m050 = target_change_adj == -.5
gen d_policy_m025 = target_change_adj == -.25
gen d_policy_0 = target_change_adj == 0
gen d_policy_025 = target_change_adj == 0.25
gen d_policy_050 = target_change_adj == 0.5

	* Create changes in the outcome for 24 month
foreach var of varlist indpro pcepi{
	foreach horizon of numlist 1/24{
		gen `var'_g`horizon' = (log(`var'[_n+`horizon']) - log(`var'[_n]))*100
	}
}

foreach var of varlist unemp try_3m try_2y try_10y ff_tar{
	foreach horizon of numlist 1/24{
		gen `var'_g`horizon' = `var'[_n+`horizon'] - `var'[_n]
	}
}
order date_m
*export delimited ../../matlab/data/matlab_file.csv,replace
save ../data/processed_data,replace

use ../data/processed_data,replace

	// Sample counts
tab d_sample1
	// Define subsets
gen d_sub_1 = (d_menu_inc == 1 & d_menu_unc == 1 &  d_menu_dec == 0 & d_sample1 == 1)
gen d_sub_2 = (d_menu_inc == 1 & d_menu_unc == 1 &  d_menu_dec == 1 & d_sample1 == 1)
gen d_sub_3 = (d_menu_inc == 1 & d_menu_unc == 0 &  d_menu_dec == 1 & d_sample1 == 1)
gen d_sub_4 = (d_menu_inc == 0 & d_menu_unc == 1 &  d_menu_dec == 1 & d_sample1 == 1)

gen d_sub_01 = (d_sub_1 == 1 | d_sub_2 == 1 | d_sub_3 == 1)
gen d_sub_00 = (d_sub_1 == 1 | d_sub_4 == 1 | d_sub_2 == 1)
gen d_sub_m1 = (d_sub_4 == 1 | d_sub_2 == 1 | d_sub_3 == 1)

tab d_sub_01 
tab d_sub_00
tab d_sub_m1

tab d_sub_4 if d_sub_01==1 

********************************************************************************
*** REPLICATION - TABLE 1 ***
sort date_m
local spec_c4 "l1_inf l2_inf  l1_diff_unemp  l2_diff_unemp"
*lag_dfedtar l1_target_change l2_target_change l3_target_change  d_meeting d_crisis " 
*local controls "scale d_y2k d_nineeleven"
*`controls'
oprobit target_change_simple `spec_c4'  if d_sub_1
local ll: di %3.2f =e(ll) 
display `ll'
margins if d_sub_1==1 , dydx(`spec_c4') 

predict yhat1-yhat2 if  d_sub_1,pr
rename yhat1 yhat_unc
rename yhat2 yhat_inc

gen d_policy_inc = ( d_policy_025 == 1 |  d_policy_050==1)
gen d_policy_unc = ( d_policy_0 == 1 )
gen d_policy_dec = ( d_policy_m025 == 1 |  d_policy_m050==1)
tab d_policy_inc if d_sub_1
tab d_policy_unc if d_sub_1

sum yhat_inc if d_policy_inc==1 & d_sub_1
sum yhat_unc if d_policy_unc==1 & d_sub_1

	* Remove observations with Pr < 0.025
foreach element in _inc _unc{
	replace yhat`element'=. if yhat`element' < 0.025 & d_policy`element'==1
}

	* Weight construction
foreach element in _inc {
	gen delta`element' = d_policy`element' / yhat`element' 
}

foreach element in _unc {
	gen delta`element' = d_policy`element' / yhat`element' 
}

sum delta_unc if d_sub_1 
sum delta_inc if d_sub_1 


	* Create auxiliary variables
foreach var of varlist indpro pcepi unemp try_3m try_2y try_10y ff_tar{
	foreach element in _inc _unc {
		foreach horizon of numlist 1/24{
			gen delta`element'`var'_g`horizon' = ///
			`var'_g`horizon'*delta`element'
		}
	}
}

	* Get estimates at different horizons
gen horizon=_n	
	// Choose policy action
local policies "inc unc"

foreach policy in `policies'{
	foreach var of varlist  indpro pcepi unemp try_3m try_2y try_10y ff_tar{
		gen b_`var'_`policy'=.
		gen se_`var'_`policy'=.
		gen ciub_`var'_`policy'=.
		gen cilb_`var'_`policy'=.
		
		foreach horizon of numlist 1/24{
display("This is the estimation policy `policy' and `var' and horizon `horizon'")
			reg  delta_`policy'`var'_g`horizon' if d_sample1==1
			capture replace b_`var'_`policy'=_b[_cons] if horizon==`horizon'
			capture replace se_`var'_`policy'=_se[_cons]  if horizon==`horizon'
			replace ciub_`var'_`policy'= b_`var'_`policy' + ///
			1.68 * se_`var'_`policy' if horizon==`horizon'
			replace cilb_`var'_`policy'= b_`var'_`policy' - ///
			1.68 * se_`var'_`policy' if horizon==`horizon'
		}
	}
}

local policies "inc unc"
foreach policy in `policies'{
	twoway scatter b_indpro_`policy' ///
	horizon if horizon<=24, ///
	c( l l l) lpattern(dash solid dash) m(i oh i) title("`policy'bp on IP") ///
	name("IP`policy'",replace) legend(off) ytitle("Change IP (in %)") ///
	ylabel(-4(.5)4,grid) 
}

merge 1:1 horizon using causal_fx_3alts



foreach var of varlist  indpro pcepi unemp try_3m try_2y try_10y ff_tar{
	gen b_`var'_causal=b_`var'_inc-b_`var'_unc
}

twoway scatter b_indpro_causal ///
horizon if horizon<=24, ///
c( l l l) lpattern(dash solid dash) m(i oh i) title("`policy'bp on IP") ///
name("IP`policy'",replace) legend(off) ytitle("Change IP (in %)") ///
ylabel(-4(.5)4,grid) 

twoway scatter b_pcepi_causal ///
horizon if horizon<=24, ///
c( l l l) lpattern(dash solid dash) m(i oh i) title("`policy'bp on IP") ///
name("IP`policy'",replace) legend(off) ytitle("Change IP (in %)") ///
ylabel(-4(.5)4,grid) 


twoway scatter b_unemp_causal ///
horizon if horizon<=24, ///
c( l l l) lpattern(dash solid dash) m(i oh i) title("`policy'bp on IP") ///
name("IP`policy'",replace) legend(off) ytitle("Change IP (in %)") ///
ylabel(-4(.5)4,grid) 

twoway scatter b_ff_tar_causal ///
horizon if horizon<=24, ///
c( l l l) lpattern(dash solid dash) m(i oh i) title("`policy'bp on IP") ///
name("IP`policy'",replace) legend(off) ytitle("Change IP (in %)") ///
ylabel(-4(.5)4,grid) 





















	
	twoway scatter b_unemp_`policy'	horizon if horizon<=24, c( l l l) ///
	lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on Unemployment") name("U`policy'",replace) ///
	legend(off) ytitle("Change Unemployment (in %)") ylabel(-.4(.2).6,grid)

	twoway scatter  b_pcepi_`policy' ///
	horizon if horizon<=24, c( l l l) lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on Inflation") name("I`policy'",replace) ///
	legend(off) ytitle("Change Inflation (in %)") ylabel(-.6(.2).4,grid)

	twoway scatter  b_ff_tar_`policy'  ///
	horizon if horizon<=24, c( l l l) lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on FFR") name("FFR`policy'",replace) ///
	legend(off) ytitle("Change on Federal Funds Rate (in %)") ///
	ylabel(-1.5(.5)1.5,grid)
		
	twoway scatter  b_try_3m_`policy'  ///
	horizon if horizon<=24, c( l l l) lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on 3m T-Bill") name("Bill3m`policy'",replace) ///
	legend(off) ytitle("Change on 3m T-Bill (in %)") ylabel(-1(.5)1,grid)
	
	twoway scatter  b_try_2y_`policy'  ///
	horizon if horizon<=24, c( l l l) lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on 2y T-Bond") name("Bond2y`policy'",replace) ///
	legend(off) ytitle("Change on 2y T-Bond (in %)") ylabel(-1(.5)1,grid)
	
	twoway scatter  b_try_10y_`policy' ///
	horizon if horizon<=24, c( l l l) lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on 10y T-Bond") name("Bond10y`policy'",replace) ///
	legend(off) ytitle("Change on 10y T-Bond (in %)") ylabel(-1(.5)1,grid)
	
}
	
graph combine I025 Im025  IP025 IPm025 U025 Um025, rows(3) ///
cols(2) ysize(4) xsize(3) name("RealOutcomes",replace) 
graph export ../output/fig_realoutcomes_`spec'.pdf,replace

graph combine Bill3m025 Bill3mm025  Bond2y025 Bond2ym025 ///
Bond10y025 Bond10ym025, rows(3) cols(2) ysize(4) xsize(3) name("TermYields",replace)
graph export ../output/fig_tryyields_`spec'.pdf,replace
	
graph combine FFR025 FFRm025, rows(1) cols(2) ysize(6) xsize(9) name("FFR",replace)
graph export ../output/fig_ffrrate_`spec'.pdf,replace	

	
