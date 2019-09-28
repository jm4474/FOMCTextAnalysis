function Model = SpecTestsDelta(Model)
yM            = Model.Diag.yMspecT;


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
   error('SpecTestsDelta not Implemented for Probit');
end

   

yM    = yM(1:end-1,:); %Lag outcome variables
e     = e(2:end,:);
Z     = Z(2:end,:);
goodp = goodp(2:end,:);
if isfield(Model,'Diag');
    score = score(2:end,:);
    dp    = dp(2:end,:);    
end


pval  = zeros(size(yM,2),1);
stat  = zeros(size(yM,2),1);
n     = size(yM,1);

Zg    = Z(goodp,:);

for i = 1:size(yM,2)
    if isfield(Model,'Diag');
            vt    = zeros(size(e(goodp,:)));
            mt    = zeros(size(e(goodp,:)));
            dphat = zeros(size(vt,2),numpar);
            for j = 1:size(e,2)
                    
                    my         = Zg/(Zg'*Zg)*Zg'*yM(goodp,i);
                    dphat(j,:) = dp(goodp,(j-1)*numpar+1:j*numpar)'*(yM(goodp,i)-my)/n;

                    mt(:,j)    = e(goodp,j).*(yM(goodp,i)-my);
                    vt(:,j)    = e(goodp,j).*(yM(goodp,i)-my)+(score(goodp,:)*VarLogit*dphat(j,:)');                   
                    
            end
            stat(i) = CompSpecTestStatm(mt,vt,Model.SpecTestWhite);
            dgf     = size(vt,2);
			pval(i) = 1 - chi2cdf(stat(i),dgf); %pvalue based on chisq with 1 deg of freedom    
     end
end

Model.SpecTest     = pval;
Model.SpecTestStat = stat;
return

    