* Author: Oliver Giesecke

	* set path
cd "/Users/olivergiesecke/Dropbox/MPCounterfactual/src/etm"


use "../AKJ_Replication/replication/data/data_replication",clear
gen date_m = mofd(date)
format date_m %tm
tempfile econdata
save `econdata'

********************************************************************************
use "full_results/MEET_min10_max1.0_iter2_thinf.dta",clear
gen date_m = mofd(start_date)
format date_m %tm
drop level_0 index d
keep if Section==2
drop if start_date == date("16sep2003","DMY")
duplicates tag date_m,gen(dup)
tab dup
merge m:1 date_m using `econdata'

reshape long topic_,i(date_m) j(nr)
rename topic_ topic_sh
drop if topic_sh==.

mlogit topic_sh  PCEH UNRATE PCEH1 UNRATE1


foreach num of numlist 0/9{
lpoly topic_`num' date_m,name(topic`num',replace)
}

lpoly topic_0 date_m





use "full_results/SPEAKERS_min10_max0.7_iter2_thinf.dta",clear
drop level_0 index
rename start_date date
gen date_m = mofd(date)
format date_m %tm
duplicates drop date_m Speaker,force
merge m:1 date_m using `econdata'
drop if _merge==2

encode Speaker,gen(speaker_id)

areg topic_1 ibn.date_m ,absorb(speaker_id)


	* Covariate linear relation

global covariates "DEAJKold PCEH PCEH1 UNRATE UNRATE1  r LastChange FOMCMeetings LastCFOMC Scale  DY2K D911 month2 month3 month4 month5 month6 month7 month8 month9 month10 month11 month12"
reg topic_0 $covariates,r
reg topic_1 $covariates,r
reg topic_5 $covariates,r

	* Multinomial logit
foreach num of numlist 0/8{
	gen dt`num't9 = log(topic_`num') -  log(topic_9)
}

foreach num of numlist 0/8{
	di "********************* Estimate for Topic `num' *********************"
	reg dt`num't9 $covariates,r
}

collapse topic_*,by(date_m)
foreach num of numlist 0/9{
twoway scatter topic_`num' date_m,name(topic`num',replace)
}









/********************************************************************************










	* merge original datasets
import excel using ../../original_code_data/JBES_OprobitSTATA_FINAL/data_guido/Macro_OPF2CRawDataPScoreVariablesStart198908End201012version3Final.xls,clear first
rename Date date
tempfile propscore
save `propscore'

import delimit using "../../original_code_data/FFT_Code Final 09292016/realvaroriginal.csv",clear
gen date = mdy(month,day,year)
format date %td
drop month day year

merge 1:1 date using `propscore',nogenerate 

	* export dataset
save ../data/data_replication,replace

export delimited "../data/data_replication.csv",replace

********************************************************************************
*** Replication based on the Angrist, Kuersteiner, Jorda ***

use ../data/data_replication,clear

gen date_m = mofd(date)
format date_m %tm
	* Define the samples
gen d_sample1=0
gen d_sample2=0
replace d_sample1 =1 if monthly("07/1989","MY")<date_m & ///
date_m <= monthly("07/2005","MY")
replace d_sample2 =1 if monthly("07/1989","MY")<date_m & ///
date_m <= monthly("12/2008","MY")


global covariates "DEAJKold PCEH PCEH1 UNRATE UNRATE1  r LastChange FOMCMeetings LastCFOMC Scale  DY2K D911 month2 month3 month4 month5 month6 month7 month8 month9 month10 month11 month12"

global covariatesbal "DEAJKold PCEH PCEH1 UNRATE UNRATE1  r LastChange"

oprobit TargetChange $covariates if d_sample1==1

margins if d_sample1==1 , dydx( DEAJKold PCEH PCEH1 UNRATE UNRATE1  r LastChange FOMCMeetings LastCFOMC) predict(pr outcome(.25)) post 
	
oprobit TargetChange $covariates if d_sample1==1

predict yhat1-yhat5 if d_sample1==1,pr
rename yhat1 yhat_m050
rename yhat2 yhat_m025
rename yhat3 yhat_0
rename yhat4 yhat_025
rename yhat5 yhat_050

	* Create dummies for outcomes
gen d_policy_m050 = TargetChange == -.5
gen d_policy_m025 = TargetChange == -.25
gen d_policy_0 = TargetChange == 0
gen d_policy_025 = TargetChange == 0.25
gen d_policy_050 = TargetChange == 0.5

	* Remove observations with Pr < 0.025
foreach element in _m050 _m025 _0 _025 _050{
	replace yhat`element'=. if yhat`element' < 0.025 & d_policy`element'==1
}

	* Weight construction
foreach element in _m050 _m025 _0 _025 _050{
	gen delta`element' = d_policy`element' / yhat`element' - d_policy_0 / yhat_0
}

	* Define variables as in Matlab file (ffed pceh ip unrate)
foreach var of varlist pceh ip{
	gen ln_`var'=log(`var')
	gen d1_ln_`var'=(ln_`var' - ln_`var'[_n-1])*100
}

foreach var of varlist ffed unrate{
	gen d1_`var'=`var'-`var'[_n-1]
}

	* Generate 24 leads of the variables
foreach var of varlist d1_ln_pceh d1_ln_ip d1_ffed d1_unrate{
	foreach lead of numlist 1/24{
		gen l`lead'_`var'= `var'[_n+`lead']
	}
}


preserve 
keep if d_sample1
tab d_policy_m050
tab d_policy_m025
tab d_policy_0
tab d_policy_025
tab d_policy_050


	* Evaluation of covariate balance
foreach var of varlist $covariatesbal{
gen `var'bal_m050 = `var' * ( 12 / 192 )  / yhat_m050 if d_policy_m050
gen `var'bal_m025 = `var' * ( 25 / 192 )  / yhat_m025 if d_policy_m025
gen `var'bal_0 = `var' * ( 132 / 192 )  / yhat_0 if d_policy_0
gen `var'bal_025 = `var' * ( 18 / 192 )  / yhat_025 if d_policy_025
gen `var'bal_050 = `var' * ( 5 / 192 )  / yhat_050 if d_policy_050
}

keep *bal_*
export delimited using ../data/covbal.csv

restore


	* Residualise the outcomes 
foreach element in _m050 _m025 _0 _025 _050{
	foreach var of varlist d1_ln_pceh d1_ln_ip d1_unrate{
		foreach lead of numlist 1/24{
			quietly reg l`lead'_`var' $covariates if d_sample1==1 ///
			& yhat`element' != . ,noconstant 
			predict  l`lead'_`var'_`element'_res if d_sample1==1 ///
			& yhat`element' != . ,residuals
		}
	}
}

	* Create auxiliary variables
foreach var of varlist d1_ln_pceh d1_ln_ip d1_unrate{
	foreach lead of numlist 1/24{
		foreach element in _m050 _m025 _0 _025 _050{
			gen delta`element'_l`lead'_`var'res = ///
			l`lead'_`var'_`element'_res*delta`element'
		}
	}
}

	* Get estimates at different horizons
gen horizon=_n	

	* Choose policy action
local policies "025 m025"

foreach policy in `policies'{
	foreach var of varlist  d1_ln_pceh d1_ln_ip d1_unrate{
		gen b_`var'_`policy'=.
		gen se_`var'_`policy'=.
		gen ciub_`var'_`policy'=.
		gen cilb_`var'_`policy'=.
}
}

	* Choose policy action
local policies "025 m025"	
foreach policy in `policies'{
	foreach var of varlist  d1_ln_pceh d1_ln_ip d1_unrate{
		foreach horizon of numlist 1/24{
			reg  delta_`policy'_l`horizon'_`var'res if d_sample1==1
			capture replace b_`var'_`policy'=_b[_cons] if horizon==`horizon'
			capture replace se_`var'_`policy'=_se[_cons]  if horizon==`horizon'
			replace ciub_`var'_`policy'= b_`var'_`policy' + ///
			1.68 * se_`var'_`policy' if horizon==`horizon'
			replace cilb_`var'_`policy'= b_`var'_`policy' - ///
			1.68 * se_`var'_`policy' if horizon==`horizon'
		}
	}
}

	* Compute cumulative changes
local policies "025 m025"	
foreach policy in `policies'{
	foreach var of varlist  d1_ln_pceh d1_ln_ip d1_unrate{
		gen b_cum_`var'_`policy'=.
		foreach cum_horizon of numlist 1/24{
			egen aux = total(b_`var'_`policy') if horizon <= `cum_horizon'
			replace b_cum_`var'_`policy' = aux if horizon == `cum_horizon'
			drop aux
		}
	}
}
set scheme s1mono,perm
local policies "025 m025"
foreach policy in `policies'{
twoway scatter b_cum_d1_ln_ip_`policy' ///
	horizon if horizon<=24, ///
	c( l l l) lpattern(dash solid dash) m(i oh i) title("`policy'bp on IP") ///
	name("IP`policy'",replace) legend(off) ytitle("Change IP (in %)") ///
	ylabel(-3(.5)1,grid) 
	
	twoway scatter b_cum_d1_unrate_`policy'	///
	horizon if horizon<=24, c( l l l) ///
	lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on Unemployment") name("U`policy'",replace) ///
	legend(off) ytitle("Change Unemployment (in %)") ylabel(-.4(.2).6,grid)

	twoway scatter  b_cum_d1_ln_pceh_`policy' ///
	horizon if horizon<=24, c( l l l) lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on Inflation") name("I`policy'",replace) ///
	legend(off) ytitle("Change Inflation (in %)") ylabel(-.6(.2).4,grid)
}	
	
	
graph combine I025 Im025  IP025 IPm025 U025 Um025, rows(3) ///
cols(2) ysize(4) xsize(3) name("RealOutcomes",replace) 
graph export ../output/replication_real.pdf,replace
