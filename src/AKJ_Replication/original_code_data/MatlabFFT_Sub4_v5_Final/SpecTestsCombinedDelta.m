function Model = SpecTestsCombinedDelta(Model)
% This version of the spec tests combines moment conditions for sevaral
% covariates into a single test

yM    = Model.Diag.yMspecT;

goodp_N25 =    Model.Diag.TestData.goodp_N25;
goodp_P25 =    Model.Diag.TestData.goodp_P25;

goodp     =    logical(goodp_N25.*goodp_P25); %only used those observations that valid both up and down

Z         =    Model.Diag.TestData.Z;

       
if isfield(Model,'VARMoneyShock')
    e = Model.VARMoneyShock;
elseif (isfield(Model,'Diag') && ~(strcmp(Model.PScore,'Multinom') && Model.numlev==2) && ...
        isfield(Model,'Diag') && ~(strcmp(Model.PScore,'Probit') && Model.numlev==2))
     e        = [Model.Diag.TestData.delta_N25,Model.Diag.TestData.delta_P25];
    dp       = [Model.Diag.TestData.h_dotN25,Model.Diag.TestData.h_dotP25];

    numpar   = Model.Diag.numpar;
    score    = Model.Diag.score;
    VarLogit = Model.Diag.VarLogit;
elseif ((isfield(Model,'Diag') && (strcmp(Model.PScore,'Multinom') && Model.numlev==2)) || ...
        (isfield(Model,'Diag') && (strcmp(Model.PScore,'Probit') && Model.numlev==2)))
    error('SpecTestsDelta not Implemented for Probit');
end

%Lag outcome variables and adjust rest of the sample   
yM    = yM(1:end-1,:); 
e     = e(2:end,:);
Z     = Z(2:end,:);
goodp = goodp(2:end,:);
if isfield(Model,'Diag');
    score = score(2:end,:);
    dp    = dp(2:end,:);    
end


n     = size(e(goodp,:),1);
J     = size(e,2);
numTestVar = size(Model.CombineTestVar,1);
vt    = zeros(n,J*numTestVar);
mt    = zeros(n,J*numTestVar);
k     = size(Model.OutcomeVarN,1);
pval  = 0;
stat  = 0;

Zg    = Z(goodp,:);

tested = false;
for i = 1:numTestVar
    dphat  = zeros(size(e,2),numpar);
    testid = strcmp(Model.OutcomeVarN,Model.CombineTestVar(i)); 
    if isfield(Model,'Diag') && ~(ones(1,k)*testid==0);
        tested    = true;
            for j = 1:J
                    my         = Zg/(Zg'*Zg)*Zg'*yM(goodp,testid);                
                    dphat(j,:) = dp(goodp,(j-1)*numpar+1:j*numpar)'*(yM(goodp,testid)-my)/n;

                    mt(:,(i-1)*J+j)    = e(goodp,j).*(yM(goodp,testid)-my);
                    vt(:,(i-1)*J+j)    = e(goodp,j).*(yM(goodp,testid)-my)+(score(goodp,:)*VarLogit*dphat(j,:)');                   

                  
            end
    end
end

if tested
    stat = CompSpecTestStatm(mt,vt,Model.SpecTestWhite);
    dgf  = size(vt,2);
    pval = 1 - chi2cdf(stat,dgf); %pvalue based on chisq with 1 deg of freedom    
end

Model.SpecTestCombined     = pval;
Model.SpecTestCombinedStat = stat;
return

    