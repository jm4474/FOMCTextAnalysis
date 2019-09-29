function RESULTS = MNLogit_SieveEstimate(INPUTS)
% -------------------------------------------------------------------------
% MNLogit_SieveEstimate
% ---------------------
% Sieve Estimation of Multinomial Logistic Regression
%
% authore : Sungho Noh
% date    : 12/3/2015
%
% INPUT(S)
% --------
% INPUTS : structure contains dataset
%       .DATA : T by k array of raw data, first column consists of discrete
%       outcomes
%       .Base_outcome : baseline outcome
%       .Order : maximum order of sieve basis functions, if zero is 
%       provided, it will estimate linear (parametric) model
%       .Initial : (optional) initial value to start iteration
%       .Display : (optional) turn on/off display
%       .SE : (optional) standard error based on (1) inverse of Hessian
%       'Hess' (2) outer product of gradient 'OuterProduct' (3) sandwich
%       form 'Robust'
%       .optim_options : (optional) MATLAB optimization toolbox options
%       .Names : (optional) names of regressors, only works for multinomial
%       logit estimation
%
% OUTPUT(S)
% ---------
% RESULTS : contains estimation results
%        .Convergence : 1 if numerical optimization finds local minimum or
%        0 if it fails
%        .y : vector of discrete outcomes used in estimation
%        .X : array of covariates (parametric) or sieve basis
%        .Beta : estimate arranged into kappa by J matrix
%        .Likelihood : log-likelihood
%        .First_Derivative : gradient arranged as the same size of psi_hat
%        .Hessian : Hessian matrix
%        .Optimiser_Settings : contains optimization settings
%
% VERSION HISTORY
% ---------------
% (09/03) can run without specifying the number of choices
% (09/07) added parametric estimation option, can be chosen by setting
% sieve_order to be zero, added display option
% (09/09) changed input/output structures to fit into DynamicHTE
% (09/10) store menu of choices outside of the likelihood function
% (09/18) modified screen outputs
% (09/29) re-ordered columns in predicted probability and its derivatives
% (10/04) altered order of arguments in phat derivatives
% (10/28) gradient (score) will be printed for each observation
% -------------------------------------------------------------------------

%% Set default values
Y = [];
X = [];
zp = [];
in = [];
max_order = 0;
disp = 0;
se = 1;
opt = optimset('GradObj','on',...                                          % use analytical gradient
               'display','off',...                                         % display option for each iteration
               'FunValCheck','on',...
               'MaxFunEvals',1e+6,...                                      % maximum number of function evaluation
               'maxiter',1e+4',...                                         % maximum number of iteration
               'tolfun',1e-4,...                                           % tolerance level for log-likelihood
               'tolx',1e-4);                                               % tolerance level for coefficients

%% Retrieve information from input values
fields = fieldnames(INPUTS);                                               % get field names
% Evaluate data entry -----------------------------------------------------
Required_DATA = find(strcmpi('DATA',fields));
if isempty(Required_DATA)
    error('Data not provided');
else
    if isnumeric(INPUTS.DATA) && size(INPUTS.DATA,1)>5 && size(INPUTS.DATA,2)>1
        Y = INPUTS.DATA(:,1);
        X = INPUTS.DATA(:,2:size(INPUTS.DATA,2));
    else
        error('Not enough number of observations');
    end
end
VNames = cell(size(X,2),1);
for ii = 1:size(X,2)
    VNames{ii} = strcat('Regressor_',num2str(ii));
end

% Evaluate baseline outcome entry -----------------------------------------
Required_zp = find(strcmpi('Base_outcome',fields));
if isempty(Required_zp)
    error('Cannot recognize baseline outcome value');
else
    zp = INPUTS.Base_outcome;
end
fields([Required_DATA,Required_zp]) = [];

for i = 1:length(fields)
    % Evaluate sieve basis option -----------------------------------------
    if strcmpi(fields{i},'Sieve_basis')
        if isempty(INPUTS.Sieve_basis)
            type = 'Poly';
        else
            type = INPUTS.Sieve_basis;
        end
    % Evaluate sieve order entry ------------------------------------------
    elseif strcmpi(fields{i},'Order')
        if isnumeric(INPUTS.Order) && length(INPUTS.Order) == 1
            max_order = round(INPUTS.Order);
        elseif isnumeric(INPUTS.Order) && length(INPUTS.Order) == 2
            max_order = [round(INPUTS.Order(1)); round(INPUTS.Order(2))];
        else
            error('Unable to read the sieve order option');
        end
    % Evaluate initial condition entry ------------------------------------
    elseif strcmpi(fields{i},'Initial')
        if isnumeric(INPUTS.Initial)
            in = INPUTS.Initial;
        else
            in = [];
        end
    % Evaluate display option entry ---------------------------------------
    elseif strcmpi(fields{i},'Display')
        if strcmp(INPUTS.Display,'all');
            disp = 2;
        elseif strcmp(INPUTS.Display,'final');
            disp = 1;
        elseif strcmp(INPUTS.Display,'off');
            disp = 0;
        else
            error('Unrecognized display option, choose between all/final/off');
        end
    % Evaluate standard error option entry --------------------------------
    elseif strcmpi(fields{i},'SE')
        if strcmp(INPUTS.SE,'Hess')
            se = 1;
        elseif strcmp(INPUTS.SE,'Outer')
            se = 2;
        elseif strcmp(INPUTS.SE,'Robust')
            se = 3;
        else
            error('Unrecognized standard error option, choose among Hess/Outer/Robust');
        end
    % Evaluate optimization control entry ---------------------------------
    elseif strcmpi(fields{i},'optim_options')
        if isempty(INPUTS.optim_options) == 0
            opt = INPUTS.optim_options;
        else
        end
    % Retrieve user-provided variable names -------------------------------
    elseif strcmpi(fields{i},'Names')
        if length(INPUTS.Names) == size(X,2)
            VNames = INPUTS.Names;
        else
        end
    end
end
VNames = ['cons_'; VNames];

%% Initiate process
if disp >= 1
    fprintf('\n');
    fprintf('Estimate discrete choice model: \n');
    fprintf('================================================================================== \n');
else
end
fprintf('\n');

%% Locate outcomes
T = size(INPUTS.DATA,1);
menu = unique(Y);
J = length(menu)-1;
base_loc = find(menu==zp);
menu = menu([base_loc,1:base_loc-1,base_loc+1:J+1]);

%% Contruct the array of regressors
if sum(max_order) == 0
    PX = [ones(T,1),X];
    k = size(PX,2);
    if disp == 2
        fprintf('Order of sieves not specified. Run parametric estimation.\n');
    else
    end
else
    [PX,k] = Generate_Sieve(X,max_order,type);
end
para_num = k*J;

%% Set initial condition
if length(in) == para_num
    if disp == 2
        fprintf('User-specified initial value used.\n');
    else
    end
elseif length(in) < para_num
    in = zeros(para_num,1);
    if disp == 2
        fprintf('Improper initial value(s). Default value will be used\n');
    else
    end
else
    in = in(1:para_num,1);
    if disp == 2
        fprintf('Too many values for the initial condition, rest will be ignored. \n');
    else
    end
end

%% Estimation
tic;
obj = @(b)MNLogit_Likelihood(b,Y,PX,J,menu,[]);                            % set objective function
if disp >= 1
    fprintf('Solving maximum of the log-likelihood... \t');
else
end
[bhat,loglik,eflag,~] = fminunc(obj,in,opt);                               % run optimization algorithm
if eflag >= 1
    fprintf('done.\n');
    b0 = bhat;
    if disp >= 1
        fprintf('Solving twice to improve the result...   \t');
    else
    end
    [bhat,loglik,eflag,~] = fminunc(obj,b0,opt);                           % run twice to improve the result
    if disp >= 1
        fprintf('done.\n');
    else
    end
else
    if disp >= 1
        fprintf('Objective function did not converge.\n');
    else
    end
end
fprintf('\n');
time = toc;

%% Prepare Results
[L,G,H,Ps,DP] = MNLogit_Likelihood(bhat,Y,PX,J,menu,1);                    % evaluate likelihood at maximum

%% Save Outputs
RESULTS = struct;
if eflag <= 0
    RESULTS.Convergence = 0;
else
    RESULTS.Convergence = 1;
end
RESULTS.Beta = reshape(bhat,[k,J]);                                    % estimates, re-arranged in matrix
RESULTS.Likelihood = -loglik;                                              % maximized log-likelihood value
RESULTS.First_Derivative = G;                                              % gradient of log-likelihood
RESULTS.Hessian = H;                                                       % Hessian of log-likelihood
RESULTS.y = Y;
RESULTS.X = PX;
if se == 1
    RESULTS.Standard_Error = reshape(sqrt(diag(inv(-H))),[k,J]);
elseif se == 2
    RESULTS.Standard_Error = reshape(sqrt(diag((G'*G)/T)),[k,J]);
else
    RESULTS.Standard_Error = reshape(sqrt(diag(inv(-H)*(G'*G)*inv(-H))),[k,J]);
end
RESULTS.t_value = RESULTS.Beta./RESULTS.Standard_Error;                    % t-values
RESULTS.phat = Ps(:,[2:base_loc,1,base_loc+1:J+1]);                        % move the column associated with the baseline outcome to its original location
DP = DP(:,:,[2:base_loc,1,base_loc+1:J+1]);                                % move the column associated with the baseline outcome to its original location
RESULTS.phat_Derivatives = permute(DP,[1,3,2]);
RESULTS.Optimiser_Settings = opt;

%% Print result
menu = menu([2:base_loc,1,base_loc+1:J+1]);
if disp == 2
    output_print = zeros(3,size(RESULTS.Beta,1),size(RESULTS.Beta,2));
    output_print(1,:,:) = RESULTS.Beta;
    output_print(2,:,:) = RESULTS.Standard_Error;
    output_print(3,:,:) = RESULTS.t_value;
    
    fprintf('\n');
    if sum(max_order) == 0
        fprintf('Multinomial Logit Estimation Output: \n');
    else
        fprintf('Sieve Nonparametric Estimation Output: \n');
    end
    fprintf('================================================================================== \n');
    fprintf('Log-likelihood at termination     \t %9.4f \n',RESULTS.Likelihood);
    fprintf('Elapsed time                      \t %9.3f sec. \n',time);
    fprintf('\n');
    fprintf('Estimated coefficients \n');
    fprintf('---------------------------------------------------------------------------------- \n');
    for i = 0:size(output_print,2)*3
        if i == 0
            fprintf('%15s \t','');
            for j = 1:J
                fprintf('  %9.2f  \t',menu(j,1));
            end
            fprintf('\n');
            fprintf('---------------------------------------------------------------------------------- \n');
        elseif i>0 && mod(i,3) == 1
            fprintf('%15s \t',VNames{floor(i/3)+1});
            for j = 1:J
                fprintf('  %9.6f  \t',output_print(1,floor(i/3)+1,j));
            end
            fprintf('\n');
        elseif i>0 && mod(i,3) == 2
            fprintf('%15s \t','');
            for j = 1:J
                fprintf(' (%9.6f) \t',output_print(2,floor(i/3)+1,j));
            end
            fprintf('\n');
        elseif i>0 && mod(i,3) == 0
            fprintf('%15s \t','');
            for j = 1:J
               fprintf(' [%9.6f] \t',output_print(3,floor(i/3),j));
            end
            fprintf('\n');
        else
        end            
    end
else
end
fprintf('================================================================================== \n');
fprintf('\n');
