function Model = SpecTestsPscoreVarCombinedDelta(Model)
% This version of the spec tests combines moment conditions for sevaral
% covariates into a single test


X     = Model.Diag.X;
Xtest = Model.Diag.Xtest;

goodp_N25 =    Model.Diag.TestData.goodp_N25;
goodp_P25 =    Model.Diag.TestData.goodp_P25;

goodp     =    logical(goodp_N25.*goodp_P25); %only used those observations that valid both up and down

Z         =    Model.Diag.TestData.Z;
       
if (isfield(Model,'Diag') && ~(strcmp(Model.PScore,'Multinom') && Model.numlev==2) && ...
        isfield(Model,'Diag') && ~(strcmp(Model.PScore,'Probit') && Model.numlev==2))

    e        = [Model.Diag.TestData.delta_N25,Model.Diag.TestData.delta_P25];
    dp       = [Model.Diag.TestData.h_dotN25,Model.Diag.TestData.h_dotP25];

    numpar   = Model.Diag.numpar;
    score    = Model.Diag.score;
    VarLogit = Model.Diag.VarLogit;
elseif ((isfield(Model,'Diag') && (strcmp(Model.PScore,'Multinom') && Model.numlev==2)) || ...
        (isfield(Model,'Diag') && (strcmp(Model.PScore,'Probit') && Model.numlev==2)))
    %if multinomial with two states=logit then only use one outcome to
    %avoid multicolinearity
    error('Not implemented for Probit');
end

   


n     = size(X(goodp,:),1);
J     = size(e,2);
numTestVar = size(Model.CombineTestVar,1);
vt    = zeros(n,J*numTestVar);
mt    = zeros(n,J*numTestVar);
Zg    = Z(goodp,:);

for i = 1:numTestVar
    dphat  = zeros(size(e,2),numpar);
    testid = strcmp(Model.SpecTestSpxVarN,Model.CombineTestVar(i)); 
    if isfield(Model,'Diag');
            for j = 1:J
                    my         = Zg/(Zg'*Zg)*Zg'*Xtest(goodp,i);                
                    dphat(j,:) = dp(goodp,(j-1)*numpar+1:j*numpar)'*(Xtest(goodp,testid)-my)/n;
                    mt(:,(i-1)*J+j)    = e(goodp,j).*(Xtest(goodp,testid)-my);
                    vt(:,(i-1)*J+j)    = e(goodp,j).*(Xtest(goodp,testid)-my)+(score(goodp,:)*VarLogit*dphat(j,:)');                   
            end
    end
end

% Compute Test Statistic and P-values
stat = CompSpecTestStatm(mt,vt,Model.SpecTestWhite);
dgf  = size(vt,2);
pval = 1 - chi2cdf(stat,dgf); %pvalue based on chisq with 1 deg of freedom    


Model.SpecTestPscoreCombined = pval;
Model.SpecTestPscoreCombinedStat = stat;
return

    