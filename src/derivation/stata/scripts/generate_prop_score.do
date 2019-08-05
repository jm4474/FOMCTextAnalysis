

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


	* Contemporaneous unemployment
gen unemployment = lagged_unemp[_n+1]
twoway line  unemployment date_m

/*
	* Detrend unemployment
gen time=_n
reg unemployment time
predict det_unemployment,r
twoway (line unemployment date_m)( line det_unemployment date_m)
*/

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

/*
gen det_unemployment_l1=det_unemployment[_n-1]
gen det_unemployment_l2=det_unemployment[_n-2]
*/

	* table 1, column (4)
local c4_spec "market_exp lagged_infl l2_infl lagged_unemp l2_unemp  target_change_last target_change_last_fomc lead_dfedtar d_meeting scale d_y2k d_nineeleven d_month_1 d_month_2 d_month_3 d_month_4 d_month_5 d_month_6 d_month_7 d_month_8 d_month_9 d_month_10 d_month_11 d_month_1_fomc d_month_2_fomc d_month_3_fomc d_month_4_fomc d_month_5_fomc d_month_6_fomc d_month_7_fomc d_month_8_fomc d_month_9_fomc d_month_10_fomc d_month_11_fomc d_month_12_fomc"	
	
oprobit ord_adj_tchange `c4_spec' if d_sample1==1 

margins if d_sample1==1 , dydx(`c4_spec') 

predict yhat1-yhat5,pr
rename yhat1 yhat_m050
rename yhat2 yhat_m025
rename yhat3 yhat_0
rename yhat4 yhat_025
rename yhat5 yhat_050

	* Create dummies for outcomes
tab target_change_adj, gen(d_policy)
rename d_policy1 d_policy_m050
rename d_policy2 d_policy_m025
rename d_policy3 d_policy_0
rename d_policy4 d_policy_025
rename d_policy5 d_policy_050

	* Remove observations with Pr < 0.025
foreach element in _m050 _m025 _0 _025 _050{
replace yhat`element'=. if yhat`element'<0.025 & d_policy`element'==1
}

	* Weight construction
foreach element in _m050 _m025 _0 _025 _050{
gen delta`element' = d_policy`element' / yhat`element' - d_policy_0 / yhat_0
}

	* Orthogonalize the weight with respect to the conditioning set
foreach element in _m050 _m025 _0 _025 _050{
reg delta`element' `c4_spec' if d_sample1==1 
predict delta_res`element',r
}
	
	* Create changes in the outcome for 24 month
foreach var of varlist indpro pcepi{
	foreach horizon of numlist 1/24{
		gen `var'_g`horizon' = log(`var'[_n+`horizon']) - log(`var'[_n])
	}
}

foreach var of varlist unemployment try_3m try_2y try_10y ff_tar{
	foreach horizon of numlist 1/24{
		gen `var'_g`horizon' = `var'[_n+`horizon'] - `var'[_n]
	}
}

	* Create auxiliary variables
foreach var of varlist indpro pcepi unemployment{
	foreach element in _m050 _m025 _0 _025 _050{
		foreach horizon of numlist 1/24{
			gen delta`element'`var'_g`horizon' = `var'_g`horizon'*delta_res`element'
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
	foreach var of varlist  indpro pcepi{
		gen b_`var'_`policy'=.
		gen se_`var'_`policy'=.
		gen ciub_`var'_`policy'=.
		gen cilb_`var'_`policy'=.
		
		foreach horizon of numlist 1/24{
			display("This is the estimation policy `policy' and `var' and horizon `horizon'")
			reg  delta_`policy'`var'_g`horizon' if d_sample1==1
			capture replace b_`var'_`policy'=_b[_cons] * 100 if horizon==`horizon'
			capture replace se_`var'_`policy'=_se[_cons] * 100 if horizon==`horizon'
			replace ciub_`var'_`policy'= b_`var'_`policy' + ///
			1.68 * se_`var'_`policy' if horizon==`horizon'
			replace cilb_`var'_`policy'= b_`var'_`policy' - ///
			1.68 * se_`var'_`policy' if horizon==`horizon'
		}
	}
}

foreach policy in `policies'{
	foreach var of varlist unemployment try_3m try_2y try_10y ff_tar{
		gen b_`var'_`policy'=.
		gen se_`var'_`policy'=.
		gen ciub_`var'_`policy'=.
		gen cilb_`var'_`policy'=.
		
		foreach horizon of numlist 1/24{
			display("This is the estimation policy `policy' and `var' and horizon `horizon'")
			reg  delta_`policy'`var'_g`horizon' if d_sample1==1
			capture replace b_`var'_`policy'=_b[_cons]  if horizon==`horizon'
			capture replace se_`var'_`policy'=_se[_cons]  if horizon==`horizon'
			replace ciub_`var'_`policy'= b_`var'_`policy' + ///
			1.68 * se_`var'_`policy' if horizon==`horizon'
			replace cilb_`var'_`policy'= b_`var'_`policy' - ///
			1.68 * se_`var'_`policy' if horizon==`horizon'
		}
	}
}

foreach policy in `policies'{
	twoway scatter ciub_indpro_`policy' b_indpro_`policy' cilb_indpro_`policy' ///
	horizon if horizon<=24, ///
	c( l l l) lpattern(dash solid dash) m(i oh i) title("`policy'bp on IP") ///
	name("IP`policy'",replace) legend(off) ytitle("Change IP (in %)")

	twoway scatter ciub_unemployment_`policy' b_unemployment_`policy' ///
	cilb_unemployment_`policy' 	horizon if horizon<=24, c( l l l) ///
	lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on Unemployment") name("U`policy'",replace) ///
	legend(off) ytitle("Change Unemployment (in %)")

	twoway scatter ciub_pcepi_`policy' b_pcepi_`policy' cilb_pcepi_`policy' ///
	horizon if horizon<=24, c( l l l) lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on Inflation") name("I`policy'",replace) ///
	legend(off) ytitle("Change Inflation (in %)")

	twoway scatter ciub_ff_tar_`policy' b_ff_tar_`policy' cilb_ff_tar_`policy' ///
	horizon if horizon<=24, c( l l l) lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on FFR") name("FFR`policy'",replace) ///
	legend(off) ytitle("Change on Federal Funds Rate (in %)")
		
	twoway scatter ciub_try_3m_`policy' b_try_3m_`policy' cilb_try_3m_`policy' ///
	horizon if horizon<=24, c( l l l) lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on 3m T-Bill") name("Bill3m`policy'",replace) ///
	legend(off) ytitle("Change on 3m T-Bill (in %)")
	
	twoway scatter ciub_try_2y_`policy' b_try_2y_`policy' cilb_try_2y_`policy' ///
	horizon if horizon<=24, c( l l l) lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on 2y T-Bond") name("Bond2y`policy'",replace) ///
	legend(off) ytitle("Change on 2y T-Bond (in %)")
	
	twoway scatter ciub_try_10y_`policy' b_try_10y_`policy' cilb_try_10y_`policy' ///
	horizon if horizon<=24, c( l l l) lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on 10y T-Bond") name("Bond10y`policy'",replace) ///
	legend(off) ytitle("Change on 10y T-Bond (in %)")
	
}
	
graph combine I025 Im025  IP025 IPm025 U025 Um025, rows(3) cols(2) ysize(4) xsize(3) name("RealOutcomes",replace)
graph export ../../../analysis/python/output/fig_realoutcomes.pdf,replace

graph combine Bill3m025 Bill3mm025  Bond2y025 Bond2ym025 Bond10y025 Bond10ym025, rows(3) cols(2) ysize(4) xsize(3) name("TermYields",replace)
graph export ../../../analysis/python/output/fig_tryyields.pdf,replace
	
graph combine FFR025 FFRm025, rows(1) cols(2) ysize(6) xsize(9) name("FFR",replace)
graph export ../../../analysis/python/output/fig_ffrrate.pdf,replace	

	
	
	
