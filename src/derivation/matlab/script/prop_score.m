% Author: Oliver Giesecke
% Purpose: Calculates the propensity score
% Data modified: 08/02/2019

cd '/Users/olivergiesecke/Dropbox/MPCounterfactual/src/derivation/matlab/script'
clear all

%%
data = readtable('../../python/output/matlab_file');

y =  data.ord_policy ;
X = table2array(data(:,{'lagged_infl','lagged_unemp','market_exp'}));

[B,dev,stats] = mnrfit(X,y,'model','ordinal','link','probit') ;