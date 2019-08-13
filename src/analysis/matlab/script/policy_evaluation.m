% Author: Oliver Giesecke
% Purpose: Calculates the propensity score
% Data modified: 08/09/2019

cd '/Users/olivergiesecke/Dropbox/MPCounterfactual/src/analysis/matlab/script'
clear all
global n_sample n_outcomes X D

%%
data = readtable('../data/matlab_file.csv');
data_names=data.Properties.VariableNames;


%% z = {T,U}

% Data Selection 
y = data.d_policy_inc(data.d_sub_1==1) ;
X = table2array(data(data.d_sub_1==1,{'l1_diff_unemp','l2_diff_unemp', 'l1_inf','l2_inf'}));
D = table2array(data(data.d_sub_1==1,{'d_policy_unc','d_policy_inc'}));
outcome='indpro';
IPg = table2array(data(data.d_sub_1==1,{strcat(outcome,'_g1'),strcat(outcome,'_g2')...
    ,strcat(outcome,'_g3'),strcat(outcome,'_g4'),strcat(outcome,'_g5'),...
    strcat(outcome,'_g6'),strcat(outcome,'_g7'),strcat(outcome,'_g8'),...
    strcat(outcome,'_g9'),strcat(outcome,'_g10'),strcat(outcome,'_g11'),...
    strcat(outcome,'_g12'),strcat(outcome,'_g13'),strcat(outcome,'_g14'),...
    strcat(outcome,'_g15'),strcat(outcome,'_g16'),strcat(outcome,'_g17'),...
    strcat(outcome,'_g18'),strcat(outcome,'_g19'),strcat(outcome,'_g20'),...
    strcat(outcome,'_g21'),strcat(outcome,'_g22'),strcat(outcome,'_g23'),...
    strcat(outcome,'_g24')}));
outcome='pcepi';
Pg = table2array(data(data.d_sub_1==1,{strcat(outcome,'_g1'),strcat(outcome,'_g2')...
    ,strcat(outcome,'_g3'),strcat(outcome,'_g4'),strcat(outcome,'_g5'),...
    strcat(outcome,'_g6'),strcat(outcome,'_g7'),strcat(outcome,'_g8'),...
    strcat(outcome,'_g9'),strcat(outcome,'_g10'),strcat(outcome,'_g11'),...
    strcat(outcome,'_g12'),strcat(outcome,'_g13'),strcat(outcome,'_g14'),...
    strcat(outcome,'_g15'),strcat(outcome,'_g16'),strcat(outcome,'_g17'),...
    strcat(outcome,'_g18'),strcat(outcome,'_g19'),strcat(outcome,'_g20'),...
    strcat(outcome,'_g21'),strcat(outcome,'_g22'),strcat(outcome,'_g23'),...
    strcat(outcome,'_g24')}));
outcome='unemp';
Ug = table2array(data(data.d_sub_1==1,{strcat(outcome,'_g1'),strcat(outcome,'_g2')...
    ,strcat(outcome,'_g3'),strcat(outcome,'_g4'),strcat(outcome,'_g5'),...
    strcat(outcome,'_g6'),strcat(outcome,'_g7'),strcat(outcome,'_g8'),...
    strcat(outcome,'_g9'),strcat(outcome,'_g10'),strcat(outcome,'_g11'),...
    strcat(outcome,'_g12'),strcat(outcome,'_g13'),strcat(outcome,'_g14'),...
    strcat(outcome,'_g15'),strcat(outcome,'_g16'),strcat(outcome,'_g17'),...
    strcat(outcome,'_g18'),strcat(outcome,'_g19'),strcat(outcome,'_g20'),...
    strcat(outcome,'_g21'),strcat(outcome,'_g22'),strcat(outcome,'_g23'),...
    strcat(outcome,'_g24')}));

n_periods=size(IPg,2);
n_sample=length(y); % 41 observations

% Get parameter of propensity score
b_opt = get_parameters(y,X);

% Get marginal effect
selector_outcome = 1;
mx_fx = get_marginal(X,y,b_opt,selector_outcome);

% Get propensity score
phat = get_propensity(X,y,b_opt);

% Contruct weights
weigths = D./phat;
mean(weigths);

% Contruct estimates
IPghat_inc_UT=1/n_sample.*weigths(:,2)'*IPg;
IPghat_unc_UT=1/n_sample.*weigths(:,1)'*IPg;
Pghat_inc_UT=1/n_sample.*weigths(:,2)'*Pg;
Pghat_unc_UT=1/n_sample.*weigths(:,1)'*Pg;
Ughat_inc_UT=1/n_sample.*weigths(:,2)'*Ug;
Ughat_unc_UT=1/n_sample.*weigths(:,1)'*Ug;

figure;
plot(1:n_periods,IPghat_inc_UT)


%% z = {D,U,T}

% Data Selection 
y = data.target_change_simple(data.d_sub_2==1) ;
X = table2array(data(data.d_sub_2==1,{'l1_diff_unemp','l2_diff_unemp', 'l1_inf','l2_inf'}));
D = table2array(data(data.d_sub_2==1,{'d_policy_dec','d_policy_unc','d_policy_inc'})); % keep order
outcome='indpro';
IPg = table2array(data(data.d_sub_2==1,{strcat(outcome,'_g1'),strcat(outcome,'_g2')...
    ,strcat(outcome,'_g3'),strcat(outcome,'_g4'),strcat(outcome,'_g5'),...
    strcat(outcome,'_g6'),strcat(outcome,'_g7'),strcat(outcome,'_g8'),...
    strcat(outcome,'_g9'),strcat(outcome,'_g10'),strcat(outcome,'_g11'),...
    strcat(outcome,'_g12'),strcat(outcome,'_g13'),strcat(outcome,'_g14'),...
    strcat(outcome,'_g15'),strcat(outcome,'_g16'),strcat(outcome,'_g17'),...
    strcat(outcome,'_g18'),strcat(outcome,'_g19'),strcat(outcome,'_g20'),...
    strcat(outcome,'_g21'),strcat(outcome,'_g22'),strcat(outcome,'_g23'),...
    strcat(outcome,'_g24')}));
outcome='pcepi';
Pg = table2array(data(data.d_sub_2==1,{strcat(outcome,'_g1'),strcat(outcome,'_g2')...
    ,strcat(outcome,'_g3'),strcat(outcome,'_g4'),strcat(outcome,'_g5'),...
    strcat(outcome,'_g6'),strcat(outcome,'_g7'),strcat(outcome,'_g8'),...
    strcat(outcome,'_g9'),strcat(outcome,'_g10'),strcat(outcome,'_g11'),...
    strcat(outcome,'_g12'),strcat(outcome,'_g13'),strcat(outcome,'_g14'),...
    strcat(outcome,'_g15'),strcat(outcome,'_g16'),strcat(outcome,'_g17'),...
    strcat(outcome,'_g18'),strcat(outcome,'_g19'),strcat(outcome,'_g20'),...
    strcat(outcome,'_g21'),strcat(outcome,'_g22'),strcat(outcome,'_g23'),...
    strcat(outcome,'_g24')}));
outcome='unemp';
Ug = table2array(data(data.d_sub_2==1,{strcat(outcome,'_g1'),strcat(outcome,'_g2')...
    ,strcat(outcome,'_g3'),strcat(outcome,'_g4'),strcat(outcome,'_g5'),...
    strcat(outcome,'_g6'),strcat(outcome,'_g7'),strcat(outcome,'_g8'),...
    strcat(outcome,'_g9'),strcat(outcome,'_g10'),strcat(outcome,'_g11'),...
    strcat(outcome,'_g12'),strcat(outcome,'_g13'),strcat(outcome,'_g14'),...
    strcat(outcome,'_g15'),strcat(outcome,'_g16'),strcat(outcome,'_g17'),...
    strcat(outcome,'_g18'),strcat(outcome,'_g19'),strcat(outcome,'_g20'),...
    strcat(outcome,'_g21'),strcat(outcome,'_g22'),strcat(outcome,'_g23'),...
    strcat(outcome,'_g24')}));

n_periods=size(IPg,2);

n_sample=length(y); % 46 observations

% Get parameter of propensity score
b_opt = get_parameters(y,X);

% Get marginal effect
selector_outcome = 1;
mx_fx = get_marginal(X,y,b_opt,selector_outcome);

% Get propensity score
phat = get_propensity(X,y,b_opt);

% Contruct weights
weigths = D./phat;
mean(weigths);

% Contruct estimates

IPghat_inc_DUT=1/n_sample.*weigths(:,3)'*IPg;
IPghat_unc_DUT=1/n_sample.*weigths(:,2)'*IPg;
IPghat_dec_DUT=1/n_sample.*weigths(:,1)'*IPg;
Pghat_inc_DUT=1/n_sample.*weigths(:,3)'*Pg;
Pghat_unc_DUT=1/n_sample.*weigths(:,2)'*Pg;
Pghat_dec_DUT=1/n_sample.*weigths(:,1)'*Pg;
Ughat_inc_DUT=1/n_sample.*weigths(:,3)'*Ug;
Ughat_unc_DUT=1/n_sample.*weigths(:,2)'*Ug;
Ughat_dec_DUT=1/n_sample.*weigths(:,1)'*Ug;


%% z = {D,U}



% Data Selection 
y = data.target_change_simple(data.d_sub_4==1) ;
X = table2array(data(data.d_sub_4==1,{'l1_diff_unemp','l2_diff_unemp', 'l1_inf','l2_inf'}));
D = table2array(data(data.d_sub_4==1,{'d_policy_dec','d_policy_unc'})); % keep order
outcome='indpro';
IPg = table2array(data(data.d_sub_4==1,{strcat(outcome,'_g1'),strcat(outcome,'_g2')...
    ,strcat(outcome,'_g3'),strcat(outcome,'_g4'),strcat(outcome,'_g5'),...
    strcat(outcome,'_g6'),strcat(outcome,'_g7'),strcat(outcome,'_g8'),...
    strcat(outcome,'_g9'),strcat(outcome,'_g10'),strcat(outcome,'_g11'),...
    strcat(outcome,'_g12'),strcat(outcome,'_g13'),strcat(outcome,'_g14'),...
    strcat(outcome,'_g15'),strcat(outcome,'_g16'),strcat(outcome,'_g17'),...
    strcat(outcome,'_g18'),strcat(outcome,'_g19'),strcat(outcome,'_g20'),...
    strcat(outcome,'_g21'),strcat(outcome,'_g22'),strcat(outcome,'_g23'),...
    strcat(outcome,'_g24')}));
outcome='pcepi';
Pg = table2array(data(data.d_sub_4==1,{strcat(outcome,'_g1'),strcat(outcome,'_g2')...
    ,strcat(outcome,'_g3'),strcat(outcome,'_g4'),strcat(outcome,'_g5'),...
    strcat(outcome,'_g6'),strcat(outcome,'_g7'),strcat(outcome,'_g8'),...
    strcat(outcome,'_g9'),strcat(outcome,'_g10'),strcat(outcome,'_g11'),...
    strcat(outcome,'_g12'),strcat(outcome,'_g13'),strcat(outcome,'_g14'),...
    strcat(outcome,'_g15'),strcat(outcome,'_g16'),strcat(outcome,'_g17'),...
    strcat(outcome,'_g18'),strcat(outcome,'_g19'),strcat(outcome,'_g20'),...
    strcat(outcome,'_g21'),strcat(outcome,'_g22'),strcat(outcome,'_g23'),...
    strcat(outcome,'_g24')}));
outcome='unemp';
Ug = table2array(data(data.d_sub_4==1,{strcat(outcome,'_g1'),strcat(outcome,'_g2')...
    ,strcat(outcome,'_g3'),strcat(outcome,'_g4'),strcat(outcome,'_g5'),...
    strcat(outcome,'_g6'),strcat(outcome,'_g7'),strcat(outcome,'_g8'),...
    strcat(outcome,'_g9'),strcat(outcome,'_g10'),strcat(outcome,'_g11'),...
    strcat(outcome,'_g12'),strcat(outcome,'_g13'),strcat(outcome,'_g14'),...
    strcat(outcome,'_g15'),strcat(outcome,'_g16'),strcat(outcome,'_g17'),...
    strcat(outcome,'_g18'),strcat(outcome,'_g19'),strcat(outcome,'_g20'),...
    strcat(outcome,'_g21'),strcat(outcome,'_g22'),strcat(outcome,'_g23'),...
    strcat(outcome,'_g24')}));

n_periods=size(IPg,2);

n_sample=length(y); % 33 observations

% Get parameter of propensity score
b_opt = get_parameters(y,X);

% Get marginal effect
selector_outcome = 1;
mx_fx = get_marginal(X,y,b_opt,selector_outcome);

% Get propensity score
phat = get_propensity(X,y,b_opt);

% Contruct weights
weigths = D./phat;
mean(weigths);

% Contruct estimates
IPghat_unc_DU=1/n_sample.*weigths(:,1)'*IPg;
IPghat_dec_DU=1/n_sample.*weigths(:,2)'*IPg;
Pghat_unc_DU=1/n_sample.*weigths(:,1)'*Pg;
Pghat_dec_DU=1/n_sample.*weigths(:,2)'*Pg;
Ughat_unc_DU=1/n_sample.*weigths(:,1)'*Ug;
Ughat_dec_DU=1/n_sample.*weigths(:,2)'*Ug;

x0=5;
y0=5;
width=1000;
height=400;

subplot(1,3,1);
plot(1:n_periods,[IPghat_unc_UT;IPghat_unc_DUT;IPghat_unc_DU])
legend('Menu UT','Menu DUT','Menu DU','Location','northwest') 
title('Policy U')
ylabel('IP in percent')
xlabel('months')
subplot(1,3,2);
plot(1:n_periods,[Pghat_unc_UT;Pghat_unc_DUT;Pghat_unc_DU])
legend('Menu UT','Menu DUT','Menu DU','Location','northwest') 
title('Policy U')
ylabel('Inflation in percent')
xlabel('months')
subplot(1,3,3);
plot(1:n_periods,[Ughat_unc_UT;Ughat_unc_DUT;Ughat_unc_DU])
legend('Menu UT','Menu DUT','Menu DU','Location','northwest') 
title('Policy U')
ylabel('Unemployment in percent')
xlabel('months')
set(gcf,'position',[x0,y0,width,height])
saveas(gcf,'../output/fig_policy_U.png')

subplot(1,3,1);
plot(1:n_periods,[IPghat_dec_DU;IPghat_dec_DUT])
legend('Menu DU','Menu DUT','Location','northwest') 
title('Policy D')
ylabel('IP in percent')
xlabel('months')
subplot(1,3,2);
plot(1:n_periods,[Pghat_dec_DU;Pghat_dec_DUT])
legend('Menu DU','Menu DUT','Location','northwest') 
title('Policy D')
ylabel('Inflation in percent')
xlabel('months')
subplot(1,3,3);
plot(1:n_periods,[Ughat_dec_DU;Ughat_dec_DUT])
legend('Menu DU','Menu DUT','Location','southwest') 
title('Policy D')
ylabel('Unemployment in percent')
xlabel('months')
set(gcf,'position',[x0,y0,width,height])
saveas(gcf,'../output/fig_policy_D.png')

subplot(1,3,1);
plot(1:n_periods,[IPghat_inc_UT;IPghat_inc_DUT])
legend('Menu UT','Menu DUT','Location','northwest') 
title('Policy T')
ylabel('IP in percent')
xlabel('months')
subplot(1,3,2);
plot(1:n_periods,[Pghat_inc_UT;Pghat_inc_DUT])
legend('Menu UT','Menu DUT','Location','northwest') 
title('Policy T')
ylabel('Inflation in percent')
xlabel('months')
subplot(1,3,3);
plot(1:n_periods,[Ughat_inc_UT;Ughat_inc_DUT])
legend('Menu UT','Menu DUT','Location','northwest') 
title('Policy T')
ylabel('Unemployment in percent')
xlabel('months')
set(gcf,'position',[x0,y0,width,height])
saveas(gcf,'../output/fig_policy_T.png')

%% Causal Effect

% Start with policy = T
n_UT=41;
n_DUT=46;
n_DU=33;


IP_fx_UT = IPghat_inc_UT - IPghat_unc_UT;
IP_fx_DUT = IPghat_inc_DUT - IPghat_unc_DUT;
IP_fx_DUT_UT =  n_UT/(n_UT+n_DUT)*IP_fx_UT + n_DUT/(n_UT+n_DUT)*IP_fx_DUT;

IP_fx_DUT_UT_DU =  n_UT / (n_UT+n_DUT) * IPghat_inc_UT + ...
    n_DUT/(n_UT+n_DUT) * IPghat_inc_DUT - ( ...
    n_UT / (n_UT + n_DUT + n_DU) * IPghat_unc_UT  + ...
    n_DUT / (n_UT + n_DUT + n_DU) * IPghat_unc_DUT + ...
    n_DU / (n_UT + n_DUT + n_DU) * IPghat_unc_DU );

P_fx_UT = Pghat_inc_UT - Pghat_unc_UT;
P_fx_DUT = Pghat_inc_DUT - Pghat_unc_DUT;
P_fx_DUT_UT =  n_UT/(n_UT+n_DUT) * P_fx_UT + n_DUT/(n_UT+n_DUT) * P_fx_DUT;

P_fx_DUT_UT_DU =  n_UT / (n_UT+n_DUT) * Pghat_inc_UT + ...
    n_DUT/(n_UT+n_DUT) * Pghat_inc_DUT - ( ...
    n_UT / (n_UT + n_DUT + n_DU) * Pghat_unc_UT  + ...
    n_DUT / (n_UT + n_DUT + n_DU) * Pghat_unc_DUT + ...
    n_DU / (n_UT + n_DUT + n_DU) * Pghat_unc_DU );

U_fx_UT = Ughat_inc_UT - Ughat_unc_UT;
U_fx_DUT = Ughat_inc_DUT - Ughat_unc_DUT;
U_fx_DUT_UT =  n_UT/(n_UT+n_DUT) * U_fx_UT + n_DUT/(n_UT+n_DUT) * U_fx_DUT;

U_fx_DUT_UT_DU =  n_UT / (n_UT+n_DUT) * Ughat_inc_UT + ...
    n_DUT / (n_UT+n_DUT) * Ughat_inc_DUT - ( ...
    n_UT / (n_UT + n_DUT + n_DU) * Ughat_unc_UT  + ...
    n_DUT / (n_UT + n_DUT + n_DU) * Ughat_unc_DUT + ...
    n_DU / (n_UT + n_DUT + n_DU) * Ughat_unc_DU );


subplot(1,3,1);
plot(1:n_periods,[IP_fx_UT;IP_fx_DUT_UT;IP_fx_DUT_UT_DU] )
legend('Menu UT' , 'Menu UT & DUT', 'Menu UT & DUT & DU')
ylabel('IP in percent')
xlabel('months')
title('Policy T')
subplot(1,3,2);
plot(1:n_periods,[P_fx_UT;P_fx_DUT_UT;P_fx_DUT_UT_DU] )
legend('Menu UT' , 'Menu UT & DUT', 'Menu UT & DUT & DU')
ylabel('Inflation in percent')
xlabel('months')
title('Policy T')
subplot(1,3,3);
plot(1:n_periods,[U_fx_UT;U_fx_DUT_UT;U_fx_DUT_UT_DU] )
legend('Menu UT' , 'Menu UT & DUT', 'Menu UT & DUT & DU')
ylabel('Unemployment in percent')
xlabel('months')
title('Policy T')
set(gcf,'position',[x0,y0,width,height])
saveas(gcf,'../output/fig_treat_policy_T.png')


% Policy = D
n_UT=41;
n_DUT=46;
n_DU=33;


IP_fx_DU = IPghat_dec_DU - IPghat_unc_DU;
IP_fx_DUT = IPghat_dec_DUT - IPghat_unc_DUT;
IP_fx_DU_DUT =  n_DU/(n_DU+n_DUT)*IP_fx_DU + n_DUT/(n_DU+n_DUT)*IP_fx_DUT;

IP_fx_DUT_UT_DU =  n_DU / (n_DU+n_DUT) * IPghat_dec_DU + ...
    n_DUT/(n_DU+n_DUT) * IPghat_dec_DUT - ( ...
    n_UT / (n_UT + n_DUT + n_DU) * IPghat_unc_UT  + ...
    n_DUT / (n_UT + n_DUT + n_DU) * IPghat_unc_DUT + ...
    n_DU / (n_UT + n_DUT + n_DU) * IPghat_unc_DU );

P_fx_DU = Pghat_dec_DU - Pghat_unc_DU;
P_fx_DUT = Pghat_dec_DUT - Pghat_unc_DUT;
P_fx_DUT_DU =  n_DU/(n_DU+n_DUT) * P_fx_DU + n_DUT/(n_DU+n_DUT) * P_fx_DUT;

P_fx_DUT_UT_DU =  n_DU / (n_DU+n_DUT) * Pghat_dec_DU + ...
    n_DUT/(n_DU+n_DUT) * Pghat_dec_DUT - ( ...
    n_UT / (n_UT + n_DUT + n_DU) * Pghat_unc_UT  + ...
    n_DUT / (n_UT + n_DUT + n_DU) * Pghat_unc_DUT + ...
    n_DU / (n_UT + n_DUT + n_DU) * Pghat_unc_DU );

U_fx_DU = Ughat_dec_DU - Ughat_unc_DU;
U_fx_DUT = Ughat_dec_DUT - Ughat_unc_DUT;
U_fx_DUT_DU =  n_DU/(n_DU+n_DUT) * U_fx_DU + n_DUT/(n_DU+n_DUT) * U_fx_DUT;

U_fx_DUT_UT_DU =  n_DU / (n_DU+n_DUT) * Ughat_dec_DU + ...
    n_DUT / (n_DU+n_DUT) * Ughat_dec_DUT - ( ...
    n_UT / (n_UT + n_DUT + n_DU) * Ughat_unc_UT  + ...
    n_DUT / (n_UT + n_DUT + n_DU) * Ughat_unc_DUT + ...
    n_DU / (n_UT + n_DUT + n_DU) * Ughat_unc_DU );


subplot(1,3,1);
plot(1:n_periods,[IP_fx_DU;IP_fx_DU_DUT;IP_fx_DUT_UT_DU] )
legend('Menu DU' , 'Menu DU & DUT', 'Menu DU & DUT & UT','Location','northwest')
ylabel('IP in percent')
xlabel('months')
title('Policy D')

subplot(1,3,2);
plot(1:n_periods,[P_fx_DU;P_fx_DUT_DU;P_fx_DUT_UT_DU] )
legend('Menu DU' , 'Menu DU & DUT', 'Menu DU & DUT & UT','Location','northwest')
ylabel('Inflation in percent')
xlabel('months')
title('Policy D')

subplot(1,3,3);
plot(1:n_periods,[U_fx_DU;U_fx_DUT_DU;U_fx_DUT_UT_DU] )
legend('Menu DU' , 'Menu DU & DUT', 'Menu UT & DUT & DU')
ylabel('Unemployment in percent')
xlabel('months')
title('Policy D')
set(gcf,'position',[x0,y0,width,height])
saveas(gcf,'../output/fig_treat_policy_D.png')





