cd "/Users/olivergiesecke/Dropbox/MPCounterfactual/src/analysis/stata/scripts/"


import excel using ../data/INDPRO.xls,clear firstrow

gen date_m = mofd(observation_date)
format date_m %tm
drop observation_date
rename INDPRO_PC1 ag_indpro
tempfile indpro
save `indpro'

import excel using ../data/PCEPI.xls,clear firstrow

gen date_m = mofd(observation_date)
format date_m %tm
drop observation_date
rename PCEPI pcepi
tempfile pcepi
save `pcepi'

********************************************************************************
*** PREPROCESSING ***

import delimited using ../../../derivation/python/output/matlab_file,clear

	* Clean date
gen statadate=date(date,"MDY",2020)
format statadate %td
gen date_m=mofd(statadate)
format date_m %tm
drop statadate date 

merge 1:1 date_m using `indpro',nogen
merge 1:1 date_m using `pcepi',nogen

	* Define the samples
gen d_sample1=0
gen d_sample2=0
replace d_sample1 =1 if monthly("07/1989","MY")<date_m & date_m <= monthly("07/2005","MY")
replace d_sample2 =1 if monthly("07/1989","MY")<date_m & date_m <= monthly("12/2008","MY")

	* define variables
sort date_m 
gen q_inflation = (log(pcepi)-log(pcepi[_n-6]))*100

gen lag_inf=q_inflation[_n-1]
replace q_inflation = lag_inf

gen lag_ag_indpro=ag_indpro[_n-1]
replace ag_indpro = lag_ag_indpro

	* detrending
gen time = _n
reg q_inflation time if d_sample1 ==1
predict q_inflation_pred, xb
reg q_inflation time if d_sample1 ==1
predict q_inflation_detrend, residuals
label var q_inflation_detrend "Inflation (detrended)"

reg ag_indpro time if d_sample1 ==1
predict ag_indpro_pred, xb
*twoway line ag_indpro ag_indpro_pred date_m if d_sample1 ==1
reg ag_indpro time if d_sample1 ==1
predict ag_indpro_detrend, residuals
label var ag_indpro_detrend "Ind. production (detrended)"
*twoway line ag_indpro_detrend date_m if d_sample1 ==1

tsset date_m
tssmooth ma ag_indpro_ma=ag_indpro,w(84)
gen ag_indpro_detrend_ma=ag_indpro-ag_indpro_ma
*twoway line ag_indpro ag_indpro_ma date_m if d_sample1 ==1

tssmooth exponential q_inflation_exp = q_inflation,parms(.05) 
gen q_inflation_exp_detrend=q_inflation - q_inflation_exp
label var q_inflation_exp_detrend "Inflation (exp. detrended)"

drop year
gen year = yofd(dofm(date_m))
twoway scatter target_change ag_indpro_detrend if d_sample1 ==1,  yline(0) xline(0) mlabel(year)


gen c_change =.
replace c_change = 1  if target_change > 0
replace c_change = -1 if target_change < 0
replace c_change = 0  if target_change ==0

	* Produce policy outcome graphs
twoway (scatter q_inflation_exp_detrend ag_indpro_detrend if c_change == 1 ///
& d_sample1 ==1,msymbol(-)  ) ///
(scatter q_inflation_exp_detrend ag_indpro_detrend if c_change == -1 & ///
d_sample1 ==1,msymbol(Oh) ) ///
(scatter q_inflation_exp_detrend ag_indpro_detrend if c_change == 0 & ///
d_sample1 ==1,msymbol(+) ) ///
, yline(0) xline(0) xlabel(-10(2)10) title("Policy Outcomes") ///
legend(order(1 "tightening" 2 "easing" 3 "unchanged"))
graph export ../output/fig_policy_outcomes_base.pdf,replace

twoway (scatter q_inflation_detrend ag_indpro_detrend if c_change == 1 ///
& d_sample1 ==1,msymbol(-)  ) ///
(scatter q_inflation_detrend ag_indpro_detrend if c_change == -1 & ///
d_sample1 ==1,msymbol(Oh) ) ///
(scatter q_inflation_detrend ag_indpro_detrend if c_change == 0 & ///
d_sample1 ==1,msymbol(+) ) ///
, yline(0) xline(0) xlabel(-10(2)10) title("Policy Outcomes") ///
legend(order(1 "tightening" 2 "easing" 3 "unchanged"))
graph export ../output/fig_policy_outcomes_alt.pdf,replace


	* Code the policy menu
gen d_no_tightening = (d_025 + d_050 + d_075)==0
gen d_no_easing = (d_m075 + d_m050 + d_m025)==0
gen d_unchchanged_only= (d_m075 + d_m050 + d_m025 +  d_025 + d_050 + d_075 ) == 0

	* Produce policy menu graphs
twoway (scatter q_inflation_exp_detrend ag_indpro_detrend if d_no_easing == 1 ///
& d_sample1 ==1 & d_meeting==1 & d_unchchanged_only==0,msymbol(-)  ) ///
(scatter q_inflation_exp_detrend ag_indpro_detrend if d_no_tightening == 1 & ///
d_sample1 ==1 & d_meeting==1  & d_unchchanged_only==0,msymbol(Oh) ) ///
(scatter q_inflation_exp_detrend ag_indpro_detrend if  ///
d_sample1 ==1 & d_meeting==1  & d_unchchanged_only==1,msymbol(+) ) ///
, yline(0) xline(0) xlabel(-10(2)10) title("Policy Menus") ///
legend(order(1 "no easing" 2 "no tightening" 3 "unchanged only")) ///
 name(base,replace)
graph export ../output/fig_policy_menus_base.pdf,replace

twoway (scatter q_inflation_detrend ag_indpro_detrend if d_no_easing == 1 ///
& d_sample1 ==1 & d_meeting==1 & d_unchchanged_only==0,msymbol(-)  ) ///
(scatter q_inflation_detrend ag_indpro_detrend if d_no_tightening == 1 & ///
d_sample1 ==1 & d_meeting==1  & d_unchchanged_only==0,msymbol(Oh) ) ///
(scatter q_inflation_detrend ag_indpro_detrend if  ///
d_sample1 ==1 & d_meeting==1  & d_unchchanged_only==1,msymbol(+) ) ///
, yline(0) xline(0) xlabel(-10(2)10) title("Policy Menus") ///
legend(order(1 "no easing" 2 "no tightening" 3 "unchanged only")) ///
 name(alt,replace)
graph export ../output/fig_policy_menus_alt.pdf,replace





