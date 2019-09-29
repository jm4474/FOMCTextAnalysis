function [OUT,INFO] = SimulateSample(SAMPLE_SIZE,varargin)
% -------------------------------------------------------------------------
% SimulateSample
% --------------
% this code generates multiple sets of random samples that can be used for
% semiparametric policy score estimation
%
%
% date : 12/10/2015
% -------------------------------------------------------------------------

%% Set default values
ky = 1;
X_mean = 1;
X_std = 0.2;
COEF = [0.5; 0.5];
CP = 1.05;
J = length(CP)+1;
kx = size(COEF,1)-1;
RHO = 0.9;
TAU = 0.33;
Hz = 24;
maxrep = 1;
rng('default');

%% Evaluate inputs
if nargin == 1
    ssize = SAMPLE_SIZE;
elseif nargin >= 2
    ssize = SAMPLE_SIZE;
    for ii = 1:length(varargin)-1
        if strcmpi(varargin{ii},'Rep')
            maxrep = varargin{ii+1};
        elseif strcmpi(varargin{ii},'Seed')
            rng(varargin{ii+1});
        elseif strcmpi(varargin{ii},'Rho')
            RHO = varargin{ii+1};
        elseif strcmpi(varargin{ii},'Horizon')
            Hz = varargin{ii+1};
        else
        end
    end
else
    error('Not enough number of input arguments');
end

%% Set controls
Burn = floor(ssize*0.2);
Pol = ones(ssize+Burn+1,1)*(0:J-1);
M = repmat([-1e+17, CP, 1e+17],ssize+Burn+1,1);
R = tril(toeplitz(sqrt(0.04.^(1:ky))));
Horizon = min(floor(ssize*0.4),Hz);

%% Generate covariates and disturbances
XX = randn(ssize+1+Burn,kx,maxrep);
EE = randn(ssize+1+Burn,ky,maxrep);

%% Begin iteration
OUT = cell(maxrep,1);
for i = 1:maxrep
    X = [ones(ssize+1+Burn,1),X_mean+squeeze(XX(:,:,i))*X_std];
    
    % Generate multinomial random numbers (discrete choices)
    % (note: ordered probit model is used)
    Phi = normcdf(M-repmat(X*COEF,1,size(M,2)));
    P = Phi(:,2:size(Phi,2)) - Phi(:,1:size(Phi,2)-1);
    P = P./(repmat(sum(P,2),1,size(P,2)));                                 % normalization
    choice = mnrnd(1,P);                                                   % repeated draw from multinomial distribution
    D = sum(Pol.*choice,2);

    % Simulate VAR(1) process
    YY = zeros(ssize+1+Burn,ky);
    eps = squeeze(EE(:,:,i))*R';
    for t = 1:ssize+Burn
        Y0 = YY(t,:)';
        Y1 = TAU*D(t+1,:)' + RHO*Y0 + eps(t+1,:)';
        YY(t+1,:) = Y1';
    end
    
    % Save outputs
    RES = struct;
    RES.Y = YY(Burn+2:ssize+1+Burn,:);                                     % outcome variable
    RES.D = D(Burn+2:ssize+1+Burn,:);                                      % discrete choice
    RES.X = X(Burn+2:ssize+1+Burn,2:kx+1);                                 % covariates, excluding constant term
    RES.Pscore = P(Burn+2:ssize+1+Burn,:);                                 % policy scores
    OUT{i} = RES;
end

%% Save outputs
if nargout == 1
    
elseif nargout == 2
    INFO = struct;
    INFO.NOutcome = ky;
    INFO.NCovariate = kx;
    INFO.NPolicy = J;
    INFO.Choices = (0:J-1)';
    INFO.Beta = COEF;
    INFO.Threshold = CP;
    INFO.TreatmentEffect = TAU;
    INFO.ARcoefficient = RHO;
    INFO.ErrorVariance = R*R';
    
    % Predicted probabilities
    QT = [0.05, 0.25, 0.50, 0.75, 0.95];                                   % pick quantiles
    X0 = [X_mean, X_mean-X_std, X_mean+X_std, norminv(QT,X_mean,X_std)];   % points where probabilities are evaluated
    XX = [ones(length(X0),1),X0'];
    P0 = normcdf(repmat(M(1,:),length(XX),1)-repmat(XX*COEF,1,size(M,2)));
    P0 = P0(:,2:size(P0,2))-P0(:,1:size(P0,2)-1);
    INFO.PredictLoc = X0';
    INFO.PredictLocString = {'E[X]', '-1SD(X)', '+1SD(X)', 'Q(0.05)', 'Q(0.25)', 'med(X)', 'Q(0.75)', 'Q(0.95)'};
    INFO.PredictProb = P0./(repmat(sum(P0,2),1,size(P0,2)));
    
    % Actual IRF
    INFO.IRF_Level = TAU*RHO.^(1:Horizon)';
    INFO.IRF_Diff = TAU*(RHO.^(1:Horizon)'-1);
    
else
    error('Too many number of output arguments');
end