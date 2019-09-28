function Model = SpecTestsPscoreVarDelta(Model)

goodp_N25 =    Model.Diag.TestData.goodp_N25;
goodp_P25 =    Model.Diag.TestData.goodp_P25;

goodp     =    logical(goodp_N25.*goodp_P25); %only used those observations that valid both up and down

Z         =    Model.Diag.TestData.Z;

X     = Model.Diag.X;
Xtest = Model.Diag.Xtest;

      
       
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


pval  = zeros(size(Xtest(goodp,:),2),1);
stat  = zeros(size(Xtest(goodp,:),2),1);
n     = size(X,1);

Zg    = Z(goodp,:);

for i = 1:size(Xtest,2)
        if isfield(Model,'Diag');
            vt    = zeros(size(e(goodp,:)));
            mt    = zeros(size(e(goodp,:)));
            dphat = zeros(size(vt,2),numpar);
            for j = 1:size(vt,2)
                    my         = Zg/(Zg'*Zg)*Zg'*Xtest(goodp,i);                
                    dphat(j,:) = dp(goodp,(j-1)*numpar+1:j*numpar)'*(Xtest(goodp,i)-my)/n;
                  
                    mt(:,j)    = e(goodp,j).*(Xtest(goodp,i)-my);
                    vt(:,j)    = e(goodp,j).*(Xtest(goodp,i)-my)+(score(goodp,:)*VarLogit*dphat(j,:)');                   
                    
            end
            stat(i) = CompSpecTestStatm(mt,vt,Model.SpecTestWhite);
            dgf     = size(vt,2);
        end 
        pval(i) = 1 - chi2cdf(stat(i),dgf); %pvalue based on chisq with 1 deg of freedom    
end

Model.SpecTestPscore     = pval;
Model.SpecTestPscoreStat = stat;
return

    