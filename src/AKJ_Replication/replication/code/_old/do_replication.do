cd "/Users/olivergiesecke/Downloads/Kuersteiner_replication/Replication/code/"

*** Merge datasets
import excel using ../data/Macro_OPF2CRawDataPScoreVariablesStart198908End201012version3Final.xls,clear first
rename Date date
tempfile propscore
save `propscore'

import delimit using ../data/realvaroriginal.csv,clear
gen date = mdy(month,day,year)
format date %td
drop month day year

merge 1:1 date using `propscore'

****************************************************************************** Replication based on the Angrist, Kuersteiner, Jorda ***

gen date_m = mofd(date)
	* Define the samples
gen d_sample1=0
gen d_sample2=0
replace d_sample1 =1 if monthly("07/1989","MY")<date_m & date_m <= monthly("07/2005","MY")
replace d_sample2 =1 if monthly("07/1989","MY")<date_m & date_m <= monthly("12/2008","MY")

oprobit TargetChange DEAJKold PCEH PCEH1 UNRATE UNRATE1  r LastChange FOMCMeetings LastCFOMC Scale  DY2K D911 month2 month3 month4 month5 month6 month7 month8 month9 month10 month11 month12  if d_sample1==1

margins if d_sample1==1 , dydx( DEAJKold PCEH PCEH1 UNRATE UNRATE1  r LastChange FOMCMeetings LastCFOMC) predict(pr outcome(.25)) post 
	
oprobit TargetChange DEAJKold PCEH PCEH1 UNRATE UNRATE1  r LastChange FOMCMeetings LastCFOMC Scale  DY2K D911 month2 month3 month4 month5 month6 month7 month8 month9 month10 month11 month12 if d_sample1==1

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

	* Orthogonalize the weight with respect to the conditioning set
foreach element in _m050 _m025 _0 _025 _050{
	reg delta`element'  PCEH PCEH1 UNRATE UNRATE1 r LastChange FOMCMeetings LastCFOMC   if d_sample1==1
	predict delta_res`element',r
}


	* Create changes in the outcome for 24 month
foreach var of varlist pceh ip{
	foreach horizon of numlist 1/24{
		gen `var'_g`horizon' = (log(`var'[_n+`horizon']) - log(`var'[_n]))*100
	}
}

foreach var of varlist  unrate {
	foreach horizon of numlist 1/24{
		gen `var'_g`horizon' = `var'[_n+`horizon'] - `var'[_n]
	}
}

	* Create auxiliary variables
foreach var of varlist pceh ip unrate{
	foreach element in _m050 _m025 _0 _025 _050{
		foreach horizon of numlist 1/24{
			gen delta`element'`var'_g`horizon' = ///
			`var'_g`horizon'*delta_res`element'
		}
	}
}



	* Get estimates at different horizons
gen horizon=_n	

	// Choose policy action
local policies "025 m025"

foreach policy in `policies'{
	foreach var of varlist  pceh ip unrate{
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
	twoway scatter b_ip_`policy' ///
	horizon if horizon<=24, ///
	c( l l l) lpattern(dash solid dash) m(i oh i) title("`policy'bp on IP") ///
	name("IP`policy'",replace) legend(off) ytitle("Change IP (in %)") ///
	ylabel(-3.5(.5)1,grid) 

	twoway scatter b_unrate_`policy'	horizon if horizon<=24, c( l l l) ///
	lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on Unemployment") name("U`policy'",replace) ///
	legend(off) ytitle("Change Unemployment (in %)") ylabel(-.4(.2).6,grid)

	twoway scatter  b_pceh_`policy' ///
	horizon if horizon<=24, c( l l l) lpattern(dash solid dash) m(i oh i) ///
	title("`policy'bp on Inflation") name("I`policy'",replace) ///
	legend(off) ytitle("Change Inflation (in %)") ylabel(-.6(.2).4,grid)
}
	
graph combine I025 Im025  IP025 IPm025 U025 Um025, rows(3) ///
cols(2) ysize(4) xsize(3) name("RealOutcomes",replace) 

