

cd "/Users/olivergiesecke/Dropbox/MPCounterfactual/src/derivation/stata/scripts"

import delimited using ../../python/output/matlab_file,clear
drop v1

oprobit ord_policy  market_exp lagged_unemp lagged_infl
predict yhat1-yhat7
