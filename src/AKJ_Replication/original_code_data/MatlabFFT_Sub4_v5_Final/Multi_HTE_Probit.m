function [Gamma,V_Gamma,V,hdot,score,dp0,dps] = Multi_HTE_Probit(y,X,actual,phat,Omega,zp,numlev,par,HTSamp,MulHTEpar)

Z = GenDeltaControls(X,MulHTEpar); 
D = actual;

if MulHTEpar.Truncate && MulHTEpar.Trimm
    error('Multi_HTE_Oprob: Cannot truncate and trim at the same time');
elseif MulHTEpar.Truncate
    lowp    = (phat<=MulHTEpar.TruncThs);
    phat    = max(phat,MulHTEpar.TruncThs);
elseif MulHTEpar.Trimm
    lowp    = (phat<=0);
    phat    = max(phat,MulHTEpar.TrimmThs);
else
    lowp    = (phat<=0.000001);
    phat    = max(phat,0.000001); % use minimal trimming to avoid NaN
end



lowp       = logical(D.*lowp); %identify observations where D=1 and p<threshold
goodp      = ~lowp;

DeletedObs = datestr(HTSamp((sum(lowp,2)>0),:));



%postiion of the element in phat where zero element sits
n      = size(y,1);
d      = size(y,2);
J      = numlev;
k      = size(par,1);
l      = size(par,2);
vt     = zeros(n,(J-1)*d);
ht     = zeros(n,(J-1)*d);
numpar = k*l;


selmhd  = eye(J-1);
selmhd  = [selmhd(:,1:zp-1),-ones(J-1,1),selmhd(:,zp:end)];

if MulHTEpar.DemeanDelta
    deltam = zeros(n,size(phat,2));
    my     = zeros(n,size(y,2),size(phat,2));
    for i = 1:size(phat,2)
      Zg           = Z(goodp(:,i),:);
      delta        = actual./phat;
      deltam(:,i)  = Z*inv(Zg'*Zg)*Zg'*delta(goodp(:,i),i);
      my(:,:,i)      = Z*inv(Zg'*Zg)*Zg'*y(goodp(:,i),:);
    end
else
    deltam    = zeros(n,1);
    my        = zeros(n,size(y,2),size(phat,2));
end
[hdot,dp]   = Probithdot(y,my,actual,X,phat,par,J,zp);
dp0         = dp(:,(zp-1)*numpar+1:zp*numpar);
dps         = dp(:,[1:(zp-1)*numpar, zp*numpar+1:end]);
score       = ProbitLikFunGrad(par,actual,X);


for i= 1:n
        deltat      = (actual(i,:)./phat(i,:))'; 
        ht(i,:)     = selmhd*((deltat*ones(1,d)).*(ones(2,1)*y(i,:)-squeeze(my(i,:,:))'));
        vt(i,:)     = (ht(i,:)' + hdot*Omega*score(i,:)')';    
end

%Compute Impulse Responses
goodpa = and(goodp(:,1),goodp(:,2));
Gamma  = mean(ht(goodpa,:));
if strcmp(MulHTEpar.CovMethod,'NW')
    V_Gamma = NeweyWest(vt(goodpa,:)-ones(n,1)*mean(vt(goodpa,:)));
elseif strcmp(MulHTEpar.CovMethod,'White')
    V_Gamma = White(vt(goodpa,:)-ones(n,1)*mean(vt(goodpa,:)));
else
    error('Multi_HTE_Probit: Standard Error method not supported - use NW or White');
end
    

%V_Gamma=NeweyWest(ht-ones(n,1)*Gamma);

dimv   = size(vt,2);
indmat = reshape([1:dimv],d,numlev-1);
for i = 1:numlev-1
    if strcmp(MulHTEpar.CovMethod,'NW')
        V(i).Gamma = NeweyWest(vt(goodp(:,i),indmat(:,i))-ones(n,1)*mean(vt(goodp(:,i),indmat(:,i))));
    elseif strcmp(MulHTEpar.CovMethod,'White')
        V(i).Gamma = White(vt(goodp(:,i),indmat(:,i))-ones(n,1)*mean(vt(goodp(:,i),indmat(:,i))));
    else
        error('Multi_HTE_Probit: Standard Error method not supported - use NW or White');
    end
    %V(i).Gamma=NeweyWest(ht(:,indmat(:,i))-ones(n,1)*Gamma(1,indmat(:,1)));
end

return