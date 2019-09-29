function P = PScore_Predict(LOC,TYPE,varargin)
% -------------------------------------------------------------------------
% PScore_Predict
% --------------
% computes policy scores at user-specified locations or some representative
% values of covariates
%
% author : Sungho Noh
% date   : 12/11/2015
% -------------------------------------------------------------------------

Nloc = size(LOC,1);
PScoreOut = varargin{1};

if strcmpi(TYPE,'Oprob')
    Beta = PScoreOut.Beta;
    CutPoints = PScoreOut.Cut_Points;
    Xb = LOC*Beta;
    mu = repmat(CutPoints',Nloc,1);
    P = [zeros(Nloc,1), normcdf(mu-repmat(Xb,1,size(mu,2))), ones(Nloc,1)];
    P = P(:,2:size(P,2)) - P(:,1:size(P,2)-1);

elseif strcmpi(TYPE,'MNlogit')
    Beta = PScoreOut.Beta;
    Xb = [ones(Nloc,1), LOC]*Beta;
    P = [ones(Nloc,1), exp(Xb)];
    P = P./repmat(sum(P,2),1,size(Beta,2)+1);

elseif strcmpi(TYPE,'Sieve');
    SieveType = varargin{2};
    Order = varargin{3};
    XX = Generate_Sieve(LOC,Order,SieveType);
    Beta = PScoreOut.Beta;
    Xb = XX*Beta;
    P = [ones(Nloc,1), exp(Xb)];
    P = P./repmat(sum(P,2),1,size(Beta,2)+1);
else
    error('Unidentified type of p-score estimator');
end


