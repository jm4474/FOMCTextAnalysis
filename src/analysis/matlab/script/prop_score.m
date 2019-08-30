% Author: Oliver Giesecke
% Purpose: Calculates the propensity score
% Data modified: 08/09/2019

cd '/Users/olivergiesecke/Dropbox/MPCounterfactual/src/analysis/matlab/script'
clear all
global n_sample n_outcomes X D

%%
data = readtable('../data/matlab_file.csv');
data_names=data.Properties.VariableNames;

y = data.ord_adj_tchange(data.d_sample1==1) ;
% Choose specification 
% ,'d_month_5','d_month_6','d_month_7','d_month_8','d_month_9','d_month_10','d_month_11',
X = table2array(data(data.d_sample1==1,{'l1_diff_unemp','l2_diff_unemp', 'l1_inf','l2_inf','scale','d_y2k','d_meeting'}));
D = table2array(data(data.d_sample1==1,{'d_policy_m050','d_policy_m025','d_policy_0','d_policy_025','d_policy_050'}));

outcome='indpro'
Yg = table2array(data(data.d_sample1==1,{strcat(outcome,'_g1'),strcat(outcome,'_g2'),strcat(outcome,'_g3'),strcat(outcome,'_g4'),strcat(outcome,'_g5'),strcat(outcome,'_g6'),strcat(outcome,'_g7'),strcat(outcome,'_g8'),strcat(outcome,'_g9'),strcat(outcome,'_g10'),strcat(outcome,'_g11'),strcat(outcome,'_g12'),strcat(outcome,'_g13'),strcat(outcome,'_g14'),strcat(outcome,'_g15')}));

%% Traditional Maximum Likelihood approach

ord_outcome = unique(y);
n_outcomes = length(ord_outcome);
n_sample=length(y);

% Initialize the coefficients
b_init = (1:n_outcomes-1)./n_outcomes;
b_init = [b_init, ones(1, size(X,2))]';

% Compute the likelihood
b_opt=fminsearch(@(x)fn_value(y,X,ord_outcome,n_outcomes,n_sample,x), b_init);

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
    marginal_out(n_outcomes)= b_marginal*normpdf(b_constant(n_outcomes-1)-X(i,:)*b_covariates);
    
    aux_sum=aux_sum+marginal_out;  
end

avgmargfx=1/n_sample* aux_sum;

%% Predict probability

b_constant=b_opt(1:n_outcomes-1);
b_covariates=b_opt(n_outcomes:end);

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
weights=zeros(n_sample,n_outcomes);
basecat_c=3;
for out=1:n_outcomes
    weights(:,out)=aux_weight(:,out)-aux_weight(:,basecat_c);
end

select_policy=2;
weight=weights(:,select_policy);
theta=1/n_sample*weight'*Yg;

figure;
plot(1:15,theta)




%% Constrained Maximum Likelihood approach


% Initialize the coefficients
b_init = b_opt;

% Compute likelihood under the constraint

% Compute the likelihood
options = optimset('TolX',1e-8);
nonlcon = @circlecon;
A = [];
b = [];
Aeq = [];
beq = [];
lb = [];
ub = [];
b_opt_con=fmincon(@(x)fn_value_con(y,X,ord_outcome,n_outcomes,n_sample,x), b_init,A,b,Aeq,beq,lb,ub,nonlcon,options);

[a,b]=circlecon(b_opt_con)

%% Average Marginal Effects - Contrained

aux_select = zeros(n_sample,n_outcomes);
for out_c = 1 : n_outcomes
    out = ord_outcome(out_c);
    aux_select(:,out_c) = y == out;
end

selector_outcome=1;
aux_sum=zeros(n_outcomes,1);
b_constant=b_opt_con(1:n_outcomes-1);
b_covariates=b_opt_con(n_outcomes:end);
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

avgmargfx_con=1/n_sample* aux_sum;

%% Predict probability

b_constant=b_opt_con(1:n_outcomes-1);
b_covariates=b_opt_con(n_outcomes:end);

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
aux_weight(aux_weight(:,5)>40,:)=0;

weights=zeros(length(aux_weight),n_outcomes);
basecat_c=3;
for out=1:n_outcomes
    weights(:,out)=aux_weight(:,out)-aux_weight(:,basecat_c);
end

select_policy=4;
weight=weights(:,select_policy);
theta=1/length(aux_weight)*weight'*Yg;

figure;
plot(1:15,theta)


