
clear
set more off
cd "U:\Helen\Jorda\AJK\JBES_OprobitSTATA_FINAL\programs"


*** Ordered Probit
local m1 PCEH UNRATE
local m2 PCEH UNRATE r LastChange LastCFOMC Scale FOMCMeetings DY2K D911 PCEH1 UNRATE1

local m3 r LastChange LastCFOMC Scale FOMCMeetings DY2K D911 DEAJKold
local m4 PCEH UNRATE r LastChange LastCFOMC Scale FOMCMeetings DY2K D911 PCEH1 UNRATE1 DEAJKold
local m5 PCEH UNRATE Crisis
local m6 PCEH UNRATE r LastChange LastCFOMC Scale FOMCMeetings DY2K D911 PCEH1 UNRATE1 Crisis
local m7 r LastChange LastCFOMC Scale FOMCMeetings DY2K D911 DEAJKold Crisis DEAJKoldXCrisis
local m8 PCEH UNRATE r LastChange LastCFOMC Scale FOMCMeetings DY2K D911 PCEH1 UNRATE1 DEAJKold Crisis DEAJKoldXCrisis

import excel ../data_guido/Macro_OPF2CRawDataPScoreVariablesStart198908End201012version3Final.xls, firstrow
	
// use i.month instead
drop month*
	
gen year = year(Date)
gen month = month(Date)
gen date = ym(year,month)
format date %tm
order Date year month

/*
// quick and dirty way to rename
ds LastChange*
local list = r(varlist)
local j = 0

foreach v of local list {
	rename `v' lc`j'
	local j = `j' + 1
	}
*/
rename TargetChange TC

forvalues i=1/8 {
	if `i'<5 {
		if `i'==1 {
		oprobit TC `m`i'' if date<ym(2005,8)
		eststo m`i'
		estadd scalar Lik = e(ll)
		local Lik = e(ll)
	
		margins, dydx(*) predict(outcome(.25)) post
		eststo mr`i'
		estadd scalar Lik = `Lik'
		}
		else {
		oprobit TC `m`i'' i.month if date<ym(2005,8)
		eststo m`i'
		estadd scalar Lik = e(ll)
		local Lik = e(ll)
		
		margins, dydx(*) predict(outcome(.25)) post
		eststo mr`i'
		estadd scalar Lik = `Lik'
		}
	}
	if `i'>4 {
		if `i'==5 {
		oprobit TC `m`i'' if date<ym(2009,1)
		eststo m`i'
		estadd scalar Lik = e(ll)
		local Lik = e(ll)
		
		margins, dydx(*) predict(outcome(.25)) post
		eststo mr`i'
		estadd scalar Lik = `Lik'
		}
		else {
		oprobit TC `m`i'' i.month if date<ym(2009,1)
		eststo m`i'
		estadd scalar Lik = e(ll)
		local Lik = e(ll)
		
		margins, dydx(*) predict(outcome(.25)) post
		eststo mr`i'
		estadd scalar Lik = `Lik'
		}
	}
}

local m8 PCEH UNRATE r LastChange LastCFOMC Scale FOMCMeetings DY2K D911 PCEH1 UNRATE1 DEAJKold Crisis DEAJKoldXCrisis
label var DEAJKold 			"FFF$ _{t}$ Pre-Crisis"
label var DEAJKoldXCrisis   "FFF$ _{t}$ Post-Crisis"
label var PCEH 				"Inflation, Lag 1"
label var PCEH1				"Inflation, Lag 2"
label var UNRATE 			"Unem. Rate, Lag 1"
label var UNRATE1			"Unem. Rate, Lag 2"
label var r 				"Target Rate"
label var LastChange 		"Last Target Change"
label var LastCFOMC 		"LTC$ \times$ FOMC"
label var FOMCMeetings		"FOMC"
label var Crisis 			"CRISIS"

label var TC TC
esttab mr1 mr2 mr3 mr4 mr5 mr6 mr7 mr8 using ../output/AJKoprobitmargins_5May2016.tex , page({geometry}) replace ///
keep(DEAJKold DEAJKoldXCrisis PCEH PCEH1 UNRATE UNRATE1 r LastChange LastCFOMC FOMCMeetings Crisis) ///
order(DEAJKold DEAJKoldXCrisis PCEH PCEH1 UNRATE UNRATE1 r LastChange LastCFOMC FOMCMeetings Crisis) ///
stats(Lik N, fmt(2 0) l("Log Likelihood" "Observations")) ///
label b(3) se(3) sfmt(3) se nogaps compress

eststo clear

