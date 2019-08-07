cd "/Users/olivergiesecke/Dropbox/MPCounterfactual/src/analysis/stata/scripts/"

import delimited using ../../../derivation/python/output/matlab_file,clear

	* Clean date
gen statadate=date(date,"MDY",2020)
format statadate %td
gen date_m=mofd(statadate)
format date_m %tm
drop statadate date 

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

	* Show overall sample stats
tab target_change if d_sample1 ==1 
// Sample size matches: 192 obs, 60 monthly changes
tab target_change if d_sample2 ==1
// Sample size matches: 232 obs, 75 monthly changes (3 changes acc.)

/*
	// QA: Graph some of the raw data for quality check
gen count = _n
gen rec_tar = 9
replace rec_tar = rec_tar[_n-1] + target_change if count != 1
gen d_check = dfedtar == rec_tar
tab d_check
*/

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
	
/*
	* Detrend unemployment
gen time=_n
reg unemployment time
predict det_unemployment,r
twoway (line unemployment date_m)( line det_unemployment date_m)
*/

	* Variable definition
gen d_y2k=monthly("12/1999","MY")==date_m 
sort date_m
gen l1_inflation = inflation[_n-1]
gen l2_inflation = inflation[_n-2]

gen l1_diff_unemp = lagged_unemp - lagged_unemp[_n-1]
gen l2_diff_unemp = l1_diff_unemp[_n-1]

gen ch=(log(pcepi)-log(pcepi[_n-1]))*100
gen l1_inf=ch[_n-1]
gen l2_inf=ch[_n-2]

	* table 1, column (1) 
local spec_c1 "l1_diff_unemp l1_inf"
oprobit ord_adj_tchange `spec_c1'   if d_sample1==1 
local ll: di %3.2f =e(ll) 
display `ll'
margins if d_sample1==1 , dydx(`spec_c1' ) 
eststo m1: margins if d_sample1==1 , dydx(`spec_c1' ) predict(pr outcome(5)) post 
estadd local loglh `ll'

// Very close match

gen l1_target_change = target_change[_n-1]
gen Fl1_target_change = l1_target_change * d_meeting

	* table 1, column (2)
local spec_c2 " l1_inf l2_inf  l1_diff_unemp  l2_diff_unemp  lag_dfedtar l1_target_change  Fl1_target_change  d_meeting" 
local controls "d_month_1 d_month_2 d_month_3 d_month_4 d_month_5 d_month_6 d_month_7 d_month_8 d_month_9 d_month_10 d_month_11 d_month_12  scale  d_y2k d_nineeleven"
oprobit ord_adj_tchange `spec_c2' `controls' if d_sample1==1 
local ll: di %3.2f =e(ll) 
display `ll'
margins if d_sample1==1 , dydx( `spec_c2' ) 
eststo m2: margins if d_sample1==1 , dydx(`spec_c2' ) predict(pr outcome(5)) post 
estadd local loglh `ll'
estadd local control "\checkmark"

	* table 1, column (4)
local spec_c4 "market_exp  l1_inf l2_inf  l1_diff_unemp  l2_diff_unemp  lag_dfedtar l1_target_change Fl1_target_change  d_meeting" 
local controls "scale d_y2k d_nineeleven d_month_1 d_month_2 d_month_3 d_month_4 d_month_5 d_month_6 d_month_7 d_month_8 d_month_9 d_month_10 d_month_11 d_month_12"
oprobit ord_adj_tchange `spec_c4' `controls' if d_sample1==1 
local ll: di %3.2f =e(ll) 
display `ll'
margins if d_sample1==1 , dydx(`spec_c4') 
eststo m3: margins if d_sample1==1 , dydx(`spec_c4' ) predict(pr outcome(5)) post 
estadd local loglh `ll'
estadd local control "\checkmark"

	*table 1 -- NEW SPECIFICATION -- 
local menu_controls "d_menu_adj_m050 d_menu_adj_m025 d_menu_adj_0 d_menu_adj_025 d_menu_adj_050"
local spec_c5 "market_exp  l1_inf l2_inf  l1_diff_unemp  l2_diff_unemp  lag_dfedtar l1_target_change Fl1_target_change  d_meeting `menu_controls'" 
local controls "scale d_y2k d_nineeleven d_month_1 d_month_2 d_month_3 d_month_4 d_month_5 d_month_6 d_month_7 d_month_8 d_month_9 d_month_10 d_month_11 d_month_12"
oprobit ord_adj_tchange `spec_c5' `controls' if d_sample1==1 
local ll: di %3.2f =e(ll) 
display `ll'
margins if d_sample1==1 , dydx(`spec_c5') 
eststo m4: margins if d_sample1==1 , dydx(`spec_c5' ) predict(pr outcome(5)) post 
estadd local loglh `ll'
estadd local control "\checkmark"

	*table 1 -- NEW SPECIFICATION V2 -- 
local menu_controls "d_menu_dec d_menu_unc d_menu_inc"
local spec_c6 "market_exp  l1_inf l2_inf  l1_diff_unemp  l2_diff_unemp  lag_dfedtar l1_target_change Fl1_target_change  d_meeting `menu_controls'" 
local controls "scale d_y2k d_nineeleven d_month_1 d_month_2 d_month_3 d_month_4 d_month_5 d_month_6 d_month_7 d_month_8 d_month_9 d_month_10 d_month_11 d_month_12"
oprobit ord_adj_tchange `spec_c6' `controls' if d_sample1==1 
local ll: di %3.2f =e(ll) 
display `ll'
margins if d_sample1==1 , dydx(`spec_c6') 
eststo m5: margins if d_sample1==1 , dydx(`spec_c6' ) predict(pr outcome(5)) post 
estadd local loglh `ll'
estadd local control "\checkmark"


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
label var Fl1_target_change "FOMC $\times$ Last Change"
label var d_meeting "FOMC"
label var d_menu_dec "Option Expansion"
label var d_menu_unc "Option No Change"
label var d_menu_inc "Option Tightening"
	
	*MAKE TABLE
#delimit;
esttab  m1 m2 m3 m4 m5 using ../output/tab_mx_effects.tex, 
replace compress b(a3) se(a3) star(* 0.10 ** 0.05 *** 0.01 ) noconstant  ///
nomtitles nogaps obslast booktabs label ///
scalar("loglh Log-likelihood" "control Controls") nonotes substitute(\_ _) ///
order(l1_inf l2_inf l1_diff_unemp l2_diff_unemp lag_dfedtar l1_target_change Fl1_target_change d_meeting );
#delimit cr

	* Select specification
local spec="spec_c4"

	***
local menu_controls "d_menu_adj_m050 d_menu_adj_m025 d_menu_adj_025 d_menu_adj_050"
local spec_c5 "market_exp  l1_inf l2_inf  l1_diff_unemp  l2_diff_unemp  lag_dfedtar l1_target_change Fl1_target_change  d_meeting" 
*local controls "scale d_y2k d_nineeleven"
*mlogit ord_adj_tchange ``spec'' `menu_controls' `controls' if d_sample1==1,baseoutcome(3)	
	***
mlogit ord_adj_tchange ``spec'' `controls' if d_sample1==1 , baseoutcome(3)

*oprobit ord_adj_tchange ``spec'' `controls' if d_sample1==1 	
predict yhat1-yhat5 if d_sample1==1,pr
rename yhat1 yhat_m050
rename yhat2 yhat_m025
rename yhat3 yhat_0
rename yhat4 yhat_025
rename yhat5 yhat_050

	* Create dummies for outcomes
gen d_policy_m050 = target_change_adj == -.5
gen d_policy_m025 = target_change_adj == -.25
gen d_policy_0 = target_change_adj == 0
gen d_policy_025 = target_change_adj == 0.25
gen d_policy_050 = target_change_adj == 0.5

	* Remove observations with Pr < 0.025
foreach element in _m050 _m025 _0 _025 _050{
	replace yhat`element'=. if yhat`element' < 0.025 & d_policy`element'==1
}

	* Weight construction
foreach element in _m050 _m025 _0 _025 _050{
	gen delta`element' = d_policy`element' / yhat`element' - d_policy_0 / yhat_0
}

	* Orthogonalize the weight with respect to the conditioning set

foreach element in _m050 _m025 _0 _025 _050{
*	reg delta`element' ``spec'' `controls'  if d_sample1==1 
*	predict delta_res`element',r
	reg delta`element' ``spec'' `controls' `menu_controls' if d_sample1==1 
	predict delta_res`element',r

}
*/
/*
foreach element in _m050 _m025 _0 _025 _050{
	gen delta_res`element' =  delta`element' 
}
*/
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

	* Create auxiliary variables
foreach var of varlist indpro pcepi unemp{
	foreach element in _m050 _m025 _0 _025 _050{
		foreach horizon of numlist 1/24{
			gen delta`element'`var'_g`horizon' = ///
			`var'_g`horizon'*delta_res`element'
		}
	}
}

foreach var of varlist  try_3m try_2y try_10y ff_tar{
	foreach element in _m050 _m025 _0 _025 _050{
		foreach horizon of numlist 1/24{
			gen delta`element'`var'_g`horizon' = `var'_g`horizon'*delta`element'
		}
	}
}

	* Get estimates at different horizons
gen horizon=_n	

	// Choose policy action
local policies "025 m025"

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

set scheme s1mono,perm
local policies "025 m025"
foreach policy in `policies'{
	twoway scatter b_indpro_`policy' ///
	horizon if horizon<=24, ///
	c( l l l) lpattern(dash solid dash) m(i oh i) title("`policy'bp on IP") ///
	name("IP`policy'",replace) legend(off) ytitle("Change IP (in %)") ///
	ylabel(-3.5(.5)1,grid) 

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

	
	
	
