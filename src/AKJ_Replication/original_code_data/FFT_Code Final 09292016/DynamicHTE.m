function Ds = DynamicHTE(y,D,zp,X,Horizon,varargin)
% ==================================================================================================================================================
% DynamicHTE
% ----------
%
% date : 9/29/2016
% Copyright: Guido M. Kuersteiner
% Written by: Guido M. Kuersteiner, Sungho Noh, Zi-Ying Mao
%
% -----------------
% REQUIRED INPUT(s)
% -----------------
% y         : array of outcome variables / size: T by ky
% D         : vector of discrete policy choice / size : T by kd
% zp        : a scalar indicator of baseline policy, should be contained in D
% X         : array of covariates for propensity score estimation / size : T by kx
% Horizon   : Maximum length of impulse-response functions.
% 
% -----------------
% OPTIONAL INPUT(s)
% -----------------
%
% 1. Policy Score Estimation Controls
% -----------------------------------
% PScore            : P-score estimation method. ("Oprob"(default) | "MNlogit" | "Sieve")
% SieveType         : Choice of sieve basis functions. Activated only when "Sieve" is chosen. ("Poly"(default) | "TriPol" | "Spline")
% SieveOrder        : Order of sieve basis. Must be numeric. Activated only when "Sieve" is chosen.
% PScoreCovMethod   : Way to compute covariance matrix for p-score. ("Hess" | "Outer"(default) | "Robust")
%
% 2. Post-estimation Analysis
% ---------------------------
% BoundMethod       : Regularization method for p-score estimates. ("Nil"(default) | "Trim" | "Truncate")
% BoundThs          : Threshold level for p-score regularization. Must be numeric.
% PredictScore      : Compute predicted scores at given values of covariates.
%                     Can be either string ("NA" (default) | "Mean" | "Standard") or numeric (user-specified locations, dimension = kx)
%
% 3. Impulse-response Estimation Controls
% ---------------------------------------
% Scale             : Scale outcome variables. Must be a numeric vector. Default is to use raw data as itself.
% Detrend           : Choose which outcomes to be detrended. ("all"(default) | "none" | user-specified string/numeric vector)
% TrendType         : To include constant vector in range space of detrending procedure ("Cons" (default) | "Linear" | "NA")
% CovMethod         : Way to compute covariance matrix for IRFs. ("NW"(default) | "White")
%
% 4. Miscellaneous
% ----------------
% Date              : Date string associated with the data. Must be a vector of strings.
% Start             : Beginning of sample. Must be included in Date. Default is to use the first observation in the data.
% End               : End of sample. Must be included in Date and cannot be prior to Start. Default is the last observation after removing Horizon+1 observations.
% OutcomeVarN       : Names of outcome variables. Must be a vector of strings, length equal to ky.
% PScoreVarN        : Names of p-score covariates. Must be a vector of strings lendth equal to kx.
%
% ---------
% OUTPUT(s)
% ---------
% All of the results are stored in a structured array "Ds" which contains the following fields:
%
% 1. Input Arguments (Ds.Inp)
% ---------------------------
% y             : array of outcome variables
% D             : discrete policy choices
% zp            : baseline policy
% X             : p-score covariates
% T             : total sample size
% y_sub         : subsample of y used in estimation, length = End date - Start date + 1
% y_subLong     : array of lead variables, size = T_sub by (ky x Horizon)
% D_sub         : subsample of D used in estimation
% X_sub         : subsample of X used in estimation
% T_sub         : length of subsample, equal to the distance between Start and End
% Policy        : menu of discrete policies, size = J x 1
% NumPolicy     : number of policies including the reference level
% PolicyChoice  : matrix of policy dummies, size = T_sub x J
% Date          : Date string (whole sample)
% Date_sub      : Date string (only used in estimation)
% OutcomeVarN   : Names of outcome variables
% PScoreVarN    : Names of p-score covariates
%
% 2. Controls (Ds.Cont)
% ---------------------
%
% 2.-1) P-Score Parameters (Ds.Cont.PSpar)
% ----------------------------------------
% Start             : Beginning of sample. Must be included in Date.
% End               : End of sample. Must be included in Date and cannot be prior to Start.
% PScore            : P-score estimation method.
% PScoreCovMethod   : Way to compute covariance matrix for p-score.
% PScorePredictLoc  : a set of covariate values where p-score estimates are computed
%
% 2.-2) HTE Parameters (Ds.Cont.HTEpar)
% -------------------------------------
% Horizon       : Maximum length of impulse-response functions.
% Truncate      : =1 if "Truncate" option is chosen. =0 otherwise.
% TruncThs      : Threshold level. =NaN if Truncate = 0.
% Trimm         : =1 if "Trim" option is chosen. =0 otherwise.
% TrimmThs      : Threshold level. =NaN if Trim = 0.
% Scale         : Vector of scale parameters, size = 1 x ky
% Detrend       : Column indices that are detrended, row vector of size 1 x ky
% TrendType     : Type of constant column in detrending, =1 if "Cons", =2 if "Linear", and empty if "NA"
% CovMethod     : Way to compute covariance matrix for IRFs.
% Dates_Bounded : String of dates where p-score estimates are regularized. Nonexists if neither of regularization methods are chosen.
% Loc_Bounded   : Index of rows where p-score estimates are regularized. Nonexists if neither of regularization methods are chosen.
%
% 3. Estimation Outputs (Ds.Out)
% ------------------------------
%
% 3.-1) P-Score Outputs (Ds.Out.PScore_result)
% --------------------------------------------
% Convergence        : binary indicator, =1 if optimization algorithm converged and =0 if not
% Beta               : contains coefficient estimates, either kx by 1 vector (Oprob) or k by J matrix (MNlogit, Sieve)
% Cut_Points         : (only for "Oprob" method) estimated thresholds
% Likelihood         : maximized log-likelihood value
% First_Derivative   : conditional likelihood score values, size of T_sub by 1
% Hessian            : Hessian matrix, dimension equal to the number of parameters
% y                  : discrete policy choices
% X                  : array of covariates
% phat               : estimated p-score for each observation, size of T_sub by J
% t_value            : t-values for parameters
% Standard_Error     : Standard error of parameters
% Optimiser_Settings : Structure containing numerical optimizer controls,
%                      See either MATLAB_Ordered_Probit_Estimate (Oprob) or MNLogit_SieveEstimate (MNlogit, Sieve) for more details
% phat_Derivatives   : derivative of p-score with respect to the parameters, evaluated at each observation. size = T_sub by J by number of parameters
% phat_predicted     : p-score estimates at the location either provided by user or a set of descriptive statistics
% phat_Bounded       : estimated p-score values after applying regularization, number of rows may be smaller than T_sub under "Truncate" option
% Weights_Residuals  : residual weights, size T_sub by J
% Covariance         : full covariance matrix for the p-score parameter estimates
% 
% 3.-2) HTE Outputs (Ds.Out.result)
% ---------------------------------
% g         : ky by 1 cell arrays of impulse-responses, each has size of Horizon by J-1
% gc        : ky by 1 cell arrays of cumulative impulse-responses, each has size of Horizon by J-1
% oo        : full covariance matrix, dimension equal to ky x Horizon x J-1 (available with White covariance or Newey-West with non-singular residual variance)
% gs        : point-wise standard error of IRF, dimension equal to g
% gcs       : point-wise standard error of cumulative IRF, dimension equal go gc 
% gsj       : covariance between IRF of policy alternatives for each outcome and horizon, dimension equal to J-1 x J-1
% gcsj      : covariance between cumulative IRF of policy alternatives for each outcome and horizon, dimension equal to J-1 x J-1
% gsjhz     : covariance between IRFs for each outcome, dimension equal to Horizon*(J-1) x Horizon*(J-1)
% gcsjhz    : covariance between cumulative IRFs for each outcome, dimension equal to Horizon*(J-1) x Horizon*(J-1) 
% 
%
% ---------------
% VERSION HISTORY
% ---------------
% 09/14/15 added multinomial logit and sieve estimation options to p-score estimation
% 09/17/15 fixed mistakes in parameter options
% 09/18/15 added truncation option, by using truncation it will change the samples used in every subsequent computations
% 09/23/15 modified IRF, cummulative IRF, and covariances
% 10/05/15 modified check out of bound option, new covariance estimation procedure
% 10/13/15 added off-diagonal entries in covariance matrix
% 10/28/15 likelihood score computed by phat_Score, modifications in covariance function
% 11/13/15 added information on Trimming/Truncation to Cont.HTEpar, predicted score locations to Cont.PSpar
% 11/30/15 modified truncation procedure and Newey-West covariance estimation function
% 12/02/15 takes outcome variables and p-score covariates names and store them for later use
% 09/14/16 added Detrend, Demean options
% 09/19/16 added t-statistics and p-values
% 09/29/16 replaced Demean to TrendType option to include linear trend case, modified residual outcome computation in IRF_breakdown and IRF_residual
% ==================================================================================================================================================
p = inputParser;

%% Required Inputs
% Following must be entered in order
addRequired(p,'y',@isnumeric);                                              % Outcomes
addRequired(p,'D',@isnumeric);                                              % Policy variable
addRequired(p,'zp',@isnumeric);                                             % Neutral policy
addRequired(p,'X',@isnumeric);                                              % Propensity score covariates
addRequired(p,'Horizon',@isnumeric);                                        % Number of leads

% Retrieve dimensions of inputs
[Ty,ky] = size(y);                                                     
[Tx,kx] = size(X);
[Td,kd] = size(D);
T = Ty;                                                                     % Time horizon of full sample

%% Optional Inputs
% Followings can be of any order, default values are used if missing
defaultBoundMethod = 'Nil';                                                 % Default no truncation/trimming
addParamValue(p,'BoundMethod',defaultBoundMethod,@ischar);                 
defaultBoundThs = 0;                                                        % Default threshold = 0
addParamValue(p,'BoundThs',@isnumeric);                                    
defaultPScore = 'Oprob';                                                    % Default P-score: Ordered Probit
addParamValue(p,'PScore',defaultPScore,@ischar);                           
defaultSieveType = 'Poly';                                                  % Default Sieve basis functions: polynomial
addParamValue(p,'SieveType',defaultSieveType,@ischar);
defaultSieveOrder = 0;                                                      % Default order of polynomials: zero order (parametric)
addParamValue(p,'SieveOrder',defaultSieveOrder,@isnumeric);
defaultCovMethod = 'NW';                                                    % Default covariance estimate: Newey-West
addParamValue(p,'CovMethod',defaultCovMethod,@ischar);
defaultPScoreCovMethod = 'Outer';                                           % Default P-score covariance estimate: Outer product of score
addParamValue(p,'PScoreCovMethod',defaultPScoreCovMethod,@ischar);
defaultPredictScore = 'NA';                                                 % Default is not to compute predicted p-scores
addParamValue(p,'PredictScore',defaultPredictScore);
defaultLeads = 'Diff';                                                      % Default way to generate lead terms: differenced variables
addParamValue(p,'Leads',defaultLeads,@ischar);
defaultDetrend = 'all';                                                     % Default choice of outcomes to be detrended: all
addParamValue(p,'Detrend',defaultDetrend);
defaultTrendType = 'Cons';                                                  % Default choice of whether to include constant term in detrending: yes
addParamValue(p,'TrendType',defaultTrendType,@ischar);
defaultScale = [];                                                          % Default choice is not to scale any of outcome variables
addParamValue(p,'Scale',defaultScale,@isnumeric)
defaultDate = cellstr(datestr(1:T));                                        % Default dates string: 1,2,...
addParamValue(p,'Date',defaultDate,@validateDate);                         
defaultOutcomeVarN = cell(ky,1);
for i = 1:ky
    defaultOutcomeVarN{i} = strcat('y',num2str(i));                         % Default outcome variable names: y1, y2, y3, ...
end
addParamValue(p,'OutcomeVarN',defaultOutcomeVarN,@iscellstr);               % Names of outcome variables
defaultPScoreVarN = cell(kx,1);
for i = 1:kx
    defaultPScoreVarN{i} = strcat('X',num2str(i));                          % Default p-score covariate names: X1, X2, X3, ...
end
addParamValue(p,'PScoreVarN',defaultPScoreVarN,@iscellstr);                 % Names of p-score covariates
defaultStart = cellstr(datestr(1)); 
addParamValue(p,'Start',defaultStart,@ischar);                              % Beginning of the sample period
defaultEnd = cellstr(datestr(T-Horizon-1));
addParamValue(p,'End',defaultEnd,@ischar);                                  % End of the sample period

%% Parse Input Parameters
parse(p,y,D,zp,X,Horizon,varargin{:});

%% Set Optional Inputs (1): Tuning Parameters
BoundMethod     = p.Results.BoundMethod;                                    % p-score bounding method
BoundThs        = p.Results.BoundThs;                                       % p-score bounding threshold
PScore          = p.Results.PScore;                                         % p-score estimation method
SieveType       = p.Results.SieveType;                                      % choice of sieve basis function
MaxOrder        = p.Results.SieveOrder;                                     % maximum order of sieves (used for "Sieve" option only)
CovMethod       = p.Results.CovMethod;                                      % choice of covariance of IRF
PScoreCovMethod = p.Results.PScoreCovMethod;                                % choice of covariance of p-score

%% Set Optional Inputs (2): Predicted Score Functions
if ischar(p.Results.PredictScore)
    if strcmpi(p.Results.PredictScore,'NA')
        ComputePredictScore = 0;
    elseif strcmpi(p.Results.PredictScore,'Mean')
        ComputePredictScore = 1;
        PredictLoc = mean(X);
        PredictLocString = 'E[X]';
    elseif strcmpi(p.Results.PredictScore,'Standard')
        ComputePredictScore = 1;
        PredictLoc = repmat(mean(X),5,1) + (-2:1:2)'*std(X);
        PredictLocString = {'-2SD(X)', '-1SD(X)', 'E[X]', '+1SD(X)', '+2SD(X)'};
    elseif strcmpi(p.Results.PredictScore,'Margins')
        ComputePredictScore = 1;
        PredictLoc = repmat(mean(X),kx+1,1) + [zeros(1,kx); diag(std(X)')];
        PredictLocString = cell(kx+1,1);
        PredictLocString{1} = 'Mean';
        for ix = 2:kx+1
            PredictLocString{ix} = strcat('+1sd(',p.Results.PScoreVarN{ix-1},')');
        end
    else
        error('Unidentified PredictScore option');
    end
elseif isnumeric(p.Results.PredictScore)
    if size(p.Results.PredictScore,2) == kx
        ComputePredictScore = 1;
        PredictLoc = p.Results.PredictScore;
        PredictLocString = 'User-specified';
    else
        error('Size of the locations provided for predicted score estimates does not match with the number of covariates');
    end
else
    error('Unidentified PredictScore option');
end

%% Set Optional Inputs (3): Related to Outcome Variables
LeadOption      = p.Results.Leads;                                          % option for constructing lead variables
if length(p.Results.OutcomeVarN) == ky
    OutcomeVarN = p.Results.OutcomeVarN;
else
    OutcomeVarN = defaultOutcomeVarN;
end
if length(p.Results.PScoreVarN) == kx
    PScoreVarN = p.Results.PScoreVarN;
else
    PScoreVarN = defaultPScoreVarN;
end
if ischar(p.Results.Detrend)
    if strcmpi(p.Results.Detrend,'all')
        OutcomesDetrended = (1:ky);
    elseif strcmpi(p.Results.Detrend,'none')
        OutcomesDetrended = [];
    else
        error('Unidentified Detrend option');
    end
elseif isnumeric(p.Results.Detrend)
    if length(p.Results.Detrend) <= ky
        OutcomesDetrended = p.Results.Detrend;
    else
        error('Number of detrending variables should be less than the total');
    end
elseif iscellstr(p.Results.Detrend)
    DetrendVarN = p.Results.Detrend;
    ky_detrend = length(DetrendVarN);
    OutcomesDetrended = zeros(1,ky);
    if ky_detrend <= ky
        for i = 1:ky_detrend
            for j = 1:ky
                if strcmpi(DetrendVarN{i},OutcomeVarN{j})
                    OutcomesDetrended(1,j) = j;
                else
                end
            end
        end
    OutcomesDetrended(OutcomesDetrended==0) = [];
    else
        error('Number of detrending variables should be less than the total');
    end
else
    error('Unidentified Detrend option');
end
if strcmpi(p.Results.TrendType,'Cons')
    TrendType = 1;
elseif strcmpi(p.Results.TrendType,'Linear')
    TrendType = 2;
elseif strcmpi(p.Results.TrendType,'NA')
    TrendType = [];
else
    error('Unidentified TrendType option');
end
if length(p.Results.Scale) == ky
    ScaleOutcomeVar = p.Results.Scale;
else
    error('Unidentified Scale option');
end

%% Set Optional Inputs (4): Scope of the Sample
Date            = p.Results.Date;                                           % date string
if length(p.Results.OutcomeVarN) == ky
    OutcomeVarN = p.Results.OutcomeVarN;
else
    OutcomeVarN = defaultOutcomeVarN;
end
if length(p.Results.PScoreVarN) == kx
    PScoreVarN = p.Results.PScoreVarN;
else
    PScoreVarN = defaultPScoreVarN;
end
Start           = p.Results.Start;                                          % start date
End             = p.Results.End;                                            % end date

%% Preparation
% Locate index of benchmark policy
menu    = unique(D);
J       = length(menu);
J0      = find(menu==zp);
if isempty(J0)
    error('Benckmark policy not found in sample!');
end

% Check if dimensions match
if Ty ~= Tx || Ty ~= Td
    error('Time dimensions do not match!');
end
if length(OutcomeVarN) ~= ky || length(PScoreVarN) ~= kx
    error('Number of variable names does not match data!');
end
if kd ~= 1
    error('Unable to take more than one policy variable!');
end

% Check if bounding threshold >= 0
if BoundThs < 0
    error('Bounding threshold must be >= 0!');
end

% Convert dates from strings to numbers
Start_num   = datenum(Start);
End_num     = datenum(End);
Date_num    = datenum(Date);

%% Create Sub-samples and Leads
% Specify start/end dates
[incStart,locStart] = ismember(Start_num,Date_num);
[incEnd,locEnd]     = ismember(End_num,Date_num);
if incStart == 0 || incEnd == 0
    error('Start/End date not in sample!');
end

% Check if horizon out of bound
if locEnd+Horizon+1 > T
    error('Input horizon out of bound!');
end

% Create sub-samples
y_sub       = y(locStart:locEnd,:);                                         % subsample of outcome variable (from start date to end date)
y_subLong   = y(locStart:(locEnd+Horizon+1),:);                             % full sample to generate lead variables
D_sub       = D(locStart:locEnd,:);                                         % policy decision, subsample of correponding size
X_sub       = X(locStart:locEnd,:);                                         % p-score covariates, subsample of corresponding size
T_sub       = length(locStart:locEnd);                                      % sample size

% Generate horizon leads of outcome variables
y_Horizon   = genLeads(y_subLong,T_sub,Horizon,LeadOption);                 % size = T_sub x (ky x Horizon)

%% Collecting Informations
% Collect relevant inputs
Ds.Inp.y            = y;
Ds.Inp.D            = D;
Ds.Inp.zp           = zp;
Ds.Inp.X            = X;
Ds.Inp.T            = T;
Ds.Inp.y_sub        = y_sub;
Ds.Inp.y_subLong    = y_subLong;
Ds.Inp.D_sub        = D_sub;
Ds.Inp.X_sub        = X_sub;
Ds.Inp.T_sub        = T_sub;
Ds.Inp.Policy       = menu;
Ds.Inp.NumPolicy    = J;
Ds.Inp.Date         = Date;                                                 % date string for the whole sample
Ds.Inp.Date_sub     = Date(locStart:locEnd);                                % date string for the subsample
Ds.Inp.OutcomeVarN  = OutcomeVarN;                                          % cell string of size ky x 1
Ds.Inp.PScoreVarN   = PScoreVarN;                                           % cell string of size kx x 1

% Collect p-score parameters
Ds.Cont.PSpar.Start     = Start;
Ds.Cont.PSpar.End       = End;
Ds.Cont.PSpar.PScore    = PScore;
Ds.Cont.PSpar.PScoreCovMethod  = PScoreCovMethod;
if ComputePredictScore == 1
    Ds.Cont.PSpar.PScorePredictLoc = PredictLocString;
else
end

% Collect HTE parameters
Ds.Cont.HTEpar.Horizon      = Horizon;
if strcmpi(BoundMethod, 'Truncate')
    Ds.Cont.HTEpar.Truncate = 1;
    Ds.Cont.HTEpar.TruncThs = BoundThs;
else
    Ds.Cont.HTEpar.Truncate = 0;
    Ds.Cont.HTEpar.TruncThs = NaN;
end
if strcmpi(BoundMethod, 'Trim')
    Ds.Cont.HTEpar.Trimm    = 1;
    Ds.Cont.HTEpar.TrimmThs = BoundThs;
else
    Ds.Cont.HTEpar.Trimm    = 0;
    Ds.Cont.HTEpar.TrimmThs = NaN;
end
Ds.Cont.HTEpar.Scale        = ScaleOutcomeVar;
Ds.Cont.HTEpar.Detrend      = OutcomesDetrended;
Ds.Cont.HTEpar.TrendType    = TrendType;
Ds.Cont.HTEpar.CovMethod    = CovMethod;

%% Estimate P-Score
PScoreInput         = struct;
PScoreInput.DATA    = [D_sub,X_sub];

% Use ordered probit estimation ===========================================
if strcmpi(PScore,'Oprob')
    PScoreInput.Display_Output_Switch = 0;
    PScoreInput.Names = PScoreVarN;
    
    % Run estimation
    PScoreOutput = MATLAB_Ordered_Probit_Estimate(PScoreInput);
    
    % Evaluate the result
    if PScoreOutput.Convergence == 0
        error('P-score estimation does not converge!');
    end
    
    % Compute derivatives of p-score
    phat_Derivatives = Oprob_derivatives(PScoreOutput);
    PhatD = zeros(T_sub,J,length(PScoreOutput.Beta)+length(PScoreOutput.Cut_Points));
    for t = 1:T_sub
        for j = 1:J
            PhatD(t,j,:) = cell2mat(phat_Derivatives(t,j));
        end
    end
    PScoreOutput.phat_Derivatives = PhatD;

% Use multinomial logit estimation ========================================    
elseif strcmpi(PScore,'MNlogit')
    PScoreInput.Display         = 'all';                                    % turn on output display
    PScoreInput.Base_outcome    = zp;                                       % indicate baseline policy
    PScoreInput.Initial         = [];                                       % set initial to be zero (uniform probability across policies)
    PScoreInput.Order           = 0;                                        % run parametric logit
    PScoreInput.SE              = PScoreCovMethod;                          % get standard error based on user-specified option
    PScoreInput.Names           = PScoreVarN;                               % names of p-score covariates
    
    % Run estimation
    PScoreOutput = MNLogit_SieveEstimate(PScoreInput);
    
    % Evaluate the result
    if PScoreOutput.Convergence == 0
        error('P-score estimation does not converge!');
    end
    
% Use nonparametric sieve estimation ======================================
elseif strcmpi(PScore,'Sieve')
    PScoreInput.Display         = 'final';                                  % turn on output display, do not print coefficients
    PScoreInput.Base_outcome    = zp;                                       % indicate baseline policy
    PScoreInput.Initial         = [];                                       % set initial to be zero (uniform probability across policies)
    PScoreInput.Sieve_basis     = SieveType;                                % choice of sieve basis functions
    PScoreInput.Order           = MaxOrder;                                 % specify sieve order
    PScoreInput.SE              = PScoreCovMethod;                          % get standard error based on user-specified option
    
    % Run estimation
    PScoreOutput = MNLogit_SieveEstimate(PScoreInput);
    
    % Evaluate the result
    if PScoreOutput.Convergence == 0
        error('P-score estimation does not converge!');
    end

% =========================================================================
else
    error('Unknown P-score model!');
end
fprintf('\n');

%% P-score Estimation: Post-estimation Analysis

% Set likelihood score
Lscore = PScoreOutput.First_Derivative;

% Compute predicted probabilities
if ComputePredictScore == 1
    if strcmpi(PScore,'Oprob')
        pscore_predict = PScore_Predict(PredictLoc,PScore,PScoreOutput);
        PScoreOutput.phat_predicted = pscore_predict;
    elseif strcmpi(PScore,'MNlogit')
        pscore_predict = PScore_Predict(PredictLoc,PScore,PScoreOutput);
        PScoreOutput.phat_predicted = pscore_predict;
    elseif strcmpi(PScore,'Sieve')
        pscore_predict = PScore_Predict(PredictLoc,PScore,PScoreOutput,SieveType,MaxOrder);
        PScoreOutput.phat_predicted = pscore_predict;
    else
        error('Unknown p-score method!');
    end
else
end

% Compute covariance matrix of policy regime
if strcmpi(PScoreCovMethod,'Outer')
    PCov = inv(Lscore'*Lscore/T_sub);
elseif strcmpi(PScoreCovMethod,'Hess')
    PCov = inv(-PScoreOutput.Hessian/T_sub);
elseif strcmpi(PScoreCovMethod,'Robust')
    PCov = T_sub*(-PScoreOutput.Hessian)\(Lscore'*Lscore)/(-PScoreOutput.Hessian);
else
    error('Unknown p-score covariance method!');
end
PScoreOutput.Covariance = PCov;


%% Truncation/Trimming
Trunc = [];
% Use full sample =========================================================
if strcmpi(BoundMethod,'Nil')
    PScoreOutput.phat_Bounded        = PScoreOutput.phat;
    Ds.Cont.HTEpar.Dates_Bounded     = {};
    Ds.Cont.HTEpar.Loc_Bounded       = [];

% Remove data when pscore is below threshold ==============================
elseif strcmpi(BoundMethod,'Truncate')
    fprintf('Bound P-score Estimates: ');
    [PhatBounded,ObsBounded,Trunc]   = PScore_Truncate(PScoreOutput.phat,D_sub,BoundThs,menu,J,J0);
    PScoreOutput.phat_Bounded        = PhatBounded;
    Ds.Cont.HTEpar.Dates_Bounded     = Date(ObsBounded,:);
    Ds.Cont.HTEpar.Loc_Bounded       = Trunc;
    fprintf('\n \n');

% Replace data when pscore is below threshold =============================
elseif strcmpi(BoundMethod,'Trim')
    fprintf('Bound P-score Estimates: ');
    [PhatBounded,ObsBounded,Ind]    = PScore_Trimm(PScoreOutput.phat,BoundThs);
    PScoreOutput.phat_Bounded       = PhatBounded;
    Ds.Cont.HTEpar.Dates_Bounded    = Date(ObsBounded,:);
    Ds.Cont.HTEpar.Loc_Bounded      = Ind;
    fprintf('\n \n');
    
% =========================================================================
else
    error('Unknown bounding method!');
end

% Collect pscore outputs
Ds.Out.PScore_result = PScoreOutput;

%% Impulse-Response Functions
fprintf('Compute impulse-response functions... \t');

% Generate dummies for policy choice
Dec = (repmat(D_sub,1,J) == repmat(menu',T_sub,1));
Ds.Inp.PolicyChoice = Dec;

% Rescale outcome variables
yy = y_Horizon.*repmat(ScaleOutcomeVar,[T_sub,Horizon]);

% Compute IRF and cummulative IRF
[ht,IRF,Ds.Out.result.g,Ds.Out.result.gc] = IRF_breakdown(yy,X_sub,PScoreOutput.phat_Bounded,...
                                                          Dec,T_sub,J,J0,Horizon,ky,Trunc,OutcomesDetrended,TrendType);
fprintf('done. \n \n');

%% Covariance Estimation (Part 1: Residuals)
% Retrieve coefficient estimates and number of coefficients
if strcmpi(PScore,'Oprob')
    psi = [PScoreOutput.Beta; PScoreOutput.Cut_Points];
    para_num = length(psi);
elseif strcmpi(PScore,'MNlogit') || strcmpi(PScore,'Sieve')
    para_num = size(PScoreOutput.Beta,1)*size(PScoreOutput.Beta,2);
else
    error('Unknown pscore method!');
end

% Compute IRF residuals
[vt,hdot,vdet] = IRF_Residual(PScoreOutput.phat_Bounded,...
                         PScoreOutput.phat_Derivatives,...
                         yy,X_sub,ht,IRF,Dec,ky,Horizon,...
                         J,J0,T_sub,Lscore,PCov,para_num,Trunc,OutcomesDetrended,TrendType);

%% Covariance Estimation (Part 2: IRF and cumulative IRF)
fprintf('Compute covariance estimate via ');

if strcmpi(CovMethod,'White')
    % White (1980) covariance estimate ====================================
    fprintf('White method... \t');
    if strcmpi(BoundMethod,'Truncate')
        vt(ObsBounded,:) = [];
        T_use = size(vt,1);
    else
        T_use = T_sub;
    end
    Ds.Out.result.oo = IRFCov_White(vt,T_use)/T_use;
    [SE,SEc,Vj,VCj,Vjhz,VCjhz] = IRFCov_breakdown(Ds.Out.result.oo,ky,Horizon,J);
    fprintf('done. \n \n');
    
elseif strcmpi(CovMethod,'NW')
    % Split cases and run Newey-West separately ===========================
    fprintf('Newey-West method... \t');
    
    % Prepare storage
    SE = cell(ky,1);
    SEc = cell(ky,1);
    Vj = cell(ky,Horizon);
    VCj = cell(ky,Horizon);
    Vjhz = cell(ky,1);
    VCjhz = cell(ky,1);
    
    % Define lower triangular matrices to cumulate variances
    MM = kron(eye(J-1),tril(ones(Horizon,Horizon)));
    Mkj = tril(ones(Horizon,Horizon));
    Mkh = tril(ones(J-1,J-1));
    
    % Set row index
    id = (1:ky*Horizon*(J-1))';
    
    for k = 1:ky
        % iterate for each outcome variable ===============================
        y_pick = zeros(ky,1);
        y_pick(k) = 1;
        id_pick = id.*(kron(kron(ones(J-1,1),ones(Horizon,1)),y_pick));
        id_pick(id_pick==0) = [];
        if strcmpi(BoundMethod,'Truncate')
            vk = vt(~ObsBounded,id_pick);
            T_use = size(vk,1);
        else
            vk = vt(:,id_pick);
            T_use = T_sub;
        end
        Ok = NeweyWest(vk-repmat(mean(vk),[T_use,1]))/T_sub;
        Vjhz{k} = Ok;
        VCjhz{k} = MM*Ok*MM';
        
        for j = 1:J-1
            % iterate for each policy =====================================
            j_pick = zeros(J-1,1);
            j_pick(j) = 1;
            id_pick = id.*(kron(kron(j_pick,ones(Horizon,1)),y_pick));
            id_pick(id_pick==0) = [];
            if strcmpi(BoundMethod,'Truncate')
                vkj = vt(~Trunc(:,j),id_pick);
                T_use = size(vkj,1);
            else
                vkj = vt(:,id_pick);
                T_use = T_sub;
            end
            Okj = NeweyWest(vkj-repmat(mean(vkj),[T_use,1]))/T_sub;
            SE{k}(:,j) = sqrt(diag(Okj));
            SEc{k}(:,j) = sqrt(diag(Mkj*Okj*Mkj'));
        end
        
        for h = 1:Horizon
            % iterate for each IRF lag ====================================
            h_pick = zeros(Horizon,1);
            h_pick(h) = 1;
            id_pick = id.*(kron(kron(ones(J-1,1),h_pick),y_pick));
            id_pick(id_pick==0) = [];
            if strcmpi(BoundMethod,'Truncate')
                vkh = vt(~ObsBounded,id_pick);
                T_use = size(vkh,1);
            else
                vkh = vt(:,id_pick);
                T_use = T_sub;
            end
            Okh = NeweyWest(vkh-repmat(mean(vkh),[T_use,1]))/T_sub;
            Vj{k,h} = Okh;
            VCj{k,h} = Mkh*Okh*Mkh';
        end
        
    end
    fprintf('done. \n');
else
    errors('Unknown covariance method!');
end

% Save outputs
Ds.Out.result.gs        = SE;                                               % point-wise standard error of IRF
Ds.Out.result.gcs       = SEc;                                              % point-wise standard error of cumulative IRF
Ds.Out.result.gsj       = Vj;                                               % covariance among IRFs of each policy alternative
Ds.Out.result.gcsj      = VCj;                                              % covariance among cumulative IRFs of each policy alternative
Ds.Out.result.gsjhz     = Vjhz;                                             % full covariance matrix of IRF for each outcome
Ds.Out.result.gcsjhz    = VCjhz;                                            % full covariance matrix of cumulative IRF for each outcome

%% T-statistics and p-values
g_t = cell(ky,1);                                                           % storage for t-stats of IRF
g_p = cell(ky,1);                                                           % storage for p-values of IRF
gc_t = cell(ky,1);                                                          % storage for t-stats of cumulative IRF
gc_p = cell(ky,1);                                                          % storage for p-values of cumulative IRF

% Compute t-statistics
for k = 1:ky
    g_t{k} = Ds.Out.result.g{k}./Ds.Out.result.gs{k};
    g_p{k} = 2*(1-normcdf(abs(g_t{k}),0,1));
    gc_t{k} = Ds.Out.result.gc{k}./Ds.Out.result.gcs{k};
    gc_p{k} = 2*(1-normcdf(abs(gc_t{k}),0,1));
end

% Save t-statistics
Ds.Out.result.t     = g_t;
Ds.Out.result.tc    = gc_t;
Ds.Out.result.p     = g_p;
Ds.Out.result.pc    = gc_p;
end