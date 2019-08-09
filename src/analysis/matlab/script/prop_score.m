% Author: Oliver Giesecke
% Purpose: Calculates the propensity score
% Data modified: 08/09/2019

cd '/Users/olivergiesecke/Dropbox/MPCounterfactual/src/analysis/matlab/script'
clear all

%%
data = readtable('../data/matlab_file.csv');
data_names=data.Properties.VariableNames;

y = data.ord_adj_tchange(data.d_sample1==1) ;
% Choose specification 
X = table2array(data(data.d_sample1==1,{'l1_diff_unemp', 'l1_inf'}));
D = table2array(data(data.d_sample1==1,{'d_policy_m050','d_policy_m025','d_policy_0','d_policy_025','d_policy_050'}));

%% Traditional Maximum Likelihood approach

ord_outcome = unique(y);
n_outcomes = length(ord_outcome);
n_sample=length(y);

% Initialize the coefficients
b_init = (1:n_outcomes-1)./n_outcomes;
b_init = [b_init, ones(1, size(X,2))]';

% Compute the likelihood
options = optimset('TolX',1e-8);
b_opt=fminsearch(@(x)fn_value(y,X,ord_outcome,n_outcomes,n_sample,x), b_init,options);

b_opt

%% Average Marginal Effects

aux_select = zeros(n_sample,n_outcomes);
for out_c = 1 : n_outcomes
    out = ord_outcome(out_c);
    aux_select(:,out_c) = y == out;
end

selector_outcome=1;
aux_sum=zeros(n_outcomes,1);
b_constant=b_opt(1:n_outcomes-1);
b_covariates=b_opt(n_outcomes:end);
b_marginal=b_covariates(selector_outcome);
for i = 1 : n_sample
    marginal_out=zeros(n_outcomes,1);
    marginal_out(1)=-b_marginal*normpdf(b_constant(1)-X(i,:)*b_covariates);       
    if n_outcomes>2
        for out_c = 2 : n_outcomes-1
            marginal_out(out_c)=-b_marginal*(normpdf(b_constant(out_c)-X(i,:)*b_covariates)...
                - normpdf(b_constant(out_c-1)-X(i,:)*b_covariates)) ;       
        end
    end
    marginal_out(n_outcomes)= b_marginal*normcdf(b_constant(n_outcomes-1)-X(i,:)*b_covariates);
    
    aux_sum=aux_sum+marginal_out;  
end

avgmargfx=1/n_sample* aux_sum;

%% Constrained Maximum Likelihood approach


% Initialize the coefficients
b_init = b_opt

% Compute likelihood under the constraint

aux_select = zeros(n_sample,n_outcomes);
for out_c = 1 : n_outcomes
    out = ord_outcome(out_c);
    aux_select(:,out_c) = y == out;
end

b_constant=b_init(1:n_outcomes-1);
b_covariates=b_init(n_outcomes:end);

% Constraint
phat=zeros(n_sample,n_outcomes);
for i = 1 : n_sample
    phat(i,1) = normcdf(b_constant(1) - X(i,:) * b_covariates);       
    if n_outcomes>2
        for out_c = 2 : n_outcomes-1
            phat(i,out_c) = normcdf(b_constant(out_c) - X(i,:) * b_covariates)...
                - normcdf(b_constant(out_c-1) - X(i,:) * b_covariates) ;       
        end
    end
    phat(i,n_outcomes) = 1 - normcdf(b_constant(n_outcomes-1) - X(i,:) * b_covariates);
end

aux_weight=D./phat;
weights=zeros(n_outcomes,1);
basecat_c=3;
for out=1:n_outcomes
    weights(out)=sum(aux_weight(:,out))-sum(aux_weight(:,basecat_c));
end

weights

% Likelihood
aux_sum=0;
for i = 1 : n_sample
    prob_out=zeros(n_outcomes,1);
    prob_out(1)=normcdf(b_constant(1)-X(i,:)*b_covariates);       
    if n_outcomes>2
        for out_c = 2 : n_outcomes-1
            prob_out(out_c)=normcdf(b_constant(out_c)-X(i,:)*b_covariates)...
                - normcdf(b_constant(out_c-1)-X(i,:)*b_covariates) ;       
        end
    end
    prob_out(n_outcomes)= 1 - normcdf(b_constant(n_outcomes-1)-X(i,:)*b_covariates);
    
    aux_sum=aux_sum+aux_select(i,:)*log(prob_out);   
end




