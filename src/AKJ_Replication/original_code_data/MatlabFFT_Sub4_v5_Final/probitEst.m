function MultiData = probitEst(y,X,yQE,level,numlev,ProScorVarN)

%{ 
Only for the binary case: this routine prodcues Probit estimates. 
 
Accuracy was tested against Stata for the 
specification:

%}

% use linear probablility model as starting values

k             = size(X,2);
n             = length(y);
oprob_results.Beta = X\y; 


[sy,ind] = sort(y);
%construct binary variables for each category

sold    = sy(1);
levInd  = sold==level;
D1      = [];
j       = 1;
for i = 2:length(y);
    if sy(i) ~= sold || i == length(y)
       D      = zeros(length(y),1);
       D(ind(j:i-1))      = ones(i-j,1);
       D1     = [D1,D];
       j      = i;
       sold   = sy(i);
       if sold == 0
            zeroind = size(D1,2)+1; %mark column with zero policy change
       end
       if i<length(y)
          levInd  = levInd + (sold==level);
       end
    end
end
D1(ind(end),end) = 1;                % this line is necessary because the loop does not catch the last entry of sy

levInd1   = levInd;
effnumlev = levInd'*ones(size(level,1),1);

if effnumlev < size(level,1)
    MultiData.ZeroP = true ; %Indicator that not all events occured in sample
end

if ~isempty(yQE)
    D1(:,zeroind) = mod(D1(:,zeroind)+yQE,2);
    D1      = [D1,yQE];
    levInd  = [levInd;true];
    levInd1 = [levInd1;true];
    effnumlev = levInd'*ones(size(level,1)+1,1);
end

if size(D1,2)>2
    error('ProbitEst not supported for multinomial case');
end

J               = size(D1,2);
par0            = oprob_results.Beta;
par0            = kron(ones(J-1,1),par0);
MultiData.y     = D1;
MultiData.X     = X;
options         = optimset('Display','iter','MaxFunEvals',15000,'GradObj','on');
if ones(length(par0),1)'*isnan(par0)>0 || par0'*par0>100
    [par1,fval,~,~,~,hessian1]  = fminunc(@(par)ProbitLikFun(par,D1,X),zeros(length(par0),1),options);
else
    [par1,fval,~,~,~,hessian1]  = fminunc(@(par)ProbitLikFun(par,D1,X),par0,options);
end
p0              = ones(1,n)*D1(:,1:end-1)/n;
[~,fvalRes,~,~,~,~]  = fminunc(@(par)ProbitLikFun(par,D1,ones(n,1)),p0,options);

par             = par1;
hessian         = hessian1;
stde            = diag(sqrt(inv(hessian)));

phat1           = ProbitPhat(par1,D1,X);
[~,grad1]       = ProbitLikFun(par1,D1,X);

phat            = phat1;
grad            = grad1;


%MultiData.pInd      = pInd;
MultiData.levInd    = levInd;
MultiData.effnumlev = effnumlev;
MultiData.Beta  = par;
MultiData.stde  = stde;
MultiData.t     = par./stde;
MultiData.pval  = 2*(1-tcdf(abs(par./stde),n-1));
MultiData.fval  = -fval;
MultiData.LR    = 2*(-fval+fvalRes);
MultiData.pvLR  = 1 - chi2cdf(MultiData.LR,size(X,2)-1);
MultiData.PR2   = 1-(-fval)/(-fvalRes);
MultiData.phat  = phat;
MultiData.grad  = grad;
MultiData.hessian = hessian;
fit             = D1.*phat1;
fit1            = (ones(length(D1),size(D1,2))-D1).*phat1;
NaNM            = NaN(size(fit));
fit(fit==0)     = NaNM(fit==0);
MultiData.fit   = fit;
MultiData.fit1  = fit1;
MultiData.VarN  = ProScorVarN;


return
